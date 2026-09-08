#!/usr/bin/env python3
"""Build the `_courses` collection from the Google Form response sheet.

Reads the published CSV export of the course-submission form, normalizes the
free-form fields, parses meeting times into structured day/time blocks, and
writes one Markdown file per course into `_courses/<semester>/`.

The generated collection is the single source of truth for both the course
index and the week calendars, so the two cannot drift apart.

Usage:
    python3 bin/fetch_courses.py            # fetch + regenerate
    python3 bin/fetch_courses.py --check    # exit 1 if output would change

Stdlib only -- no pip install needed in CI.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import shutil
import sys
import urllib.request

SHEET_ID = "1eQNUUhpCNfRubZQe0e80TT3__zau2lynrHm7dNpfoRs"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSES_DIR = os.path.join(REPO_ROOT, "_courses")
UNIVERSITIES_YML = os.path.join(REPO_ROOT, "_data", "universities.yml")

# Semesters in academic-year order. Anything else is appended alphabetically.
SEMESTER_ORDER = ["Fall", "Spring"]

# Fallback colors handed to universities we have no brand color for yet.
FALLBACK_COLORS = ["#2f6f4e", "#8a5a00", "#155e75", "#6b2d5c", "#7a3b12", "#3d4f7c"]

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri"]

# Longest-first so "Thursdays" wins over "Th", and "Th" over "T".
DAY_TOKENS = [
    ("mondays", 0), ("monday", 0), ("mon", 0),
    ("tuesdays", 1), ("tuesday", 1), ("tues", 1), ("tue", 1),
    ("wednesdays", 2), ("wednesday", 2), ("weds", 2), ("wed", 2),
    ("thursdays", 3), ("thursday", 3), ("thurs", 3), ("thur", 3), ("thu", 3),
    ("fridays", 4), ("friday", 4), ("fri", 4),
    ("th", 3), ("tu", 1), ("r", 3), ("m", 0), ("w", 2), ("f", 4), ("t", 1),
]
DAY_RE = re.compile("|".join(tok for tok, _ in DAY_TOKENS))
DAY_LOOKUP = dict(DAY_TOKENS)

# Filler words that appear between the day and the time.
FILLER_RE = re.compile(r"\b(?:from|at|on|and|starting|meets?|weekly|every)\b")

TIME = r"(?:\d{1,2}[:.]\d{2}|\d{3,4}|\d{1,2})\s*(?:[ap]\.?m?\.?)?"
RANGE_RE = re.compile(
    rf"(?P<start>{TIME})\s*(?:-{{1,2}}|–|—|\bto\b|\buntil\b)\s*(?P<end>{TIME})",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(
    r"(?P<digits>\d{1,2}[:.]\d{2}|\d{3,4}|\d{1,2})\s*(?P<ap>[ap])?", re.IGNORECASE
)


# --------------------------------------------------------------------------
# Meeting-time parsing
# --------------------------------------------------------------------------

def _parse_token(tok: str):
    """Return (hour, minute, meridiem or None) for a single time token."""
    m = TOKEN_RE.match(tok.strip())
    if not m:
        return None
    digits = m.group("digits")
    ap = (m.group("ap") or "").lower() or None
    if ":" in digits or "." in digits:
        hh, mm = re.split(r"[:.]", digits)
    elif len(digits) in (3, 4):
        hh, mm = digits[:-2], digits[-2:]
    else:
        hh, mm = digits, "0"
    hour, minute = int(hh), int(mm)
    if hour > 23 or minute > 59:
        return None
    return hour, minute, ap


def _apply(hour: int, meridiem: str) -> int:
    if meridiem == "p":
        return hour if hour == 12 else hour + 12
    return 0 if hour == 12 else hour


def _resolve_range(start_tok: str, end_tok: str):
    """Turn two time tokens into (start_minutes, end_minutes) past midnight.

    Meridiems are often only given on the end time ("3.45-4.35p"), or omitted
    entirely ("415-615"). Propagate what we know, then fall back to the
    convention that an hour before 8 means afternoon for a graduate course.
    """
    a, b = _parse_token(start_tok), _parse_token(end_tok)
    if not a or not b:
        return None
    h1, m1, ap1 = a
    h2, m2, ap2 = b

    if ap1 and ap2:
        s, e = _apply(h1, ap1), _apply(h2, ap2)
    elif ap2:  # end is explicit -- assume the start shares it
        e = _apply(h2, ap2)
        s = _apply(h1, ap2)
        if s > e:  # e.g. "11-1p": the start must be the other half of the day
            s = _apply(h1, "a" if ap2 == "p" else "p")
    elif ap1:
        s = _apply(h1, ap1)
        e = _apply(h2, ap1)
        if e < s:
            e = _apply(h2, "p" if ap1 == "a" else "a")
    else:
        s = h1 + 12 if h1 < 8 else h1
        e = h2 + 12 if h2 < 8 else h2

    start, end = s * 60 + m1, e * 60 + m2
    if end <= start:
        end += 12 * 60  # last-ditch: the end ran past noon/midnight
    if end <= start or end > 24 * 60:
        return None
    return start, end


def _parse_days(text: str):
    """Pull day indices out of the text preceding a time range."""
    cleaned = FILLER_RE.sub(" ", text.lower())
    cleaned = re.sub(r"[^a-z]+", " ", cleaned)
    days = []
    for chunk in cleaned.split():
        # A chunk counts only if it is *entirely* day tokens ("mw", "tuth").
        # Partial matches would read "Lecture" as Tuesday and "hybrid" as
        # Thursday, inventing meetings that were never submitted.
        pos, found = 0, []
        while pos < len(chunk):
            m = DAY_RE.match(chunk, pos)
            if not m:
                found = None
                break
            found.append(DAY_LOOKUP[m.group(0)])
            pos = m.end()
        for idx in found or []:
            if idx not in days:
                days.append(idx)
    return sorted(days)


def parse_meetings(raw: str):
    """Parse a free-form meeting-time string into structured blocks.

    Returns (meetings, unparsed_segments). Every segment we cannot read is
    reported back so the caller can surface it rather than dropping it.
    """
    if not raw or not raw.strip():
        return [], []

    meetings, unparsed = [], []
    for segment in re.split(r"[;]", raw):
        segment = segment.strip()
        if not segment:
            continue

        # Parentheticals are notes ("Lab", "hybrid"), not schedule data.
        notes = [n.strip() for n in re.findall(r"\(([^)]*)\)", segment)]
        body = re.sub(r"\([^)]*\)", " ", segment)

        rng = RANGE_RE.search(body)
        if not rng:
            unparsed.append(segment)
            continue

        days = _parse_days(body[: rng.start()])
        if not days:
            days = _parse_days(body[rng.end():])
        resolved = _resolve_range(rng.group("start"), rng.group("end"))
        if not days or not resolved:
            unparsed.append(segment)
            continue

        start, end = resolved
        label = "; ".join(notes)
        for day in days:
            meetings.append(
                {
                    "day_index": day,
                    "day_name": DAY_NAMES[day],
                    "day_abbr": DAY_ABBR[day],
                    "start_minutes": start,
                    "end_minutes": end,
                    "start": fmt_time(start),
                    "end": fmt_time(end),
                    "label": label,
                }
            )
    return meetings, unparsed


def fmt_time(minutes: int) -> str:
    hour, minute = divmod(minutes, 60)
    suffix = "am" if hour < 12 else "pm"
    display = hour % 12 or 12
    return f"{display}:{minute:02d}{suffix}"


# --------------------------------------------------------------------------
# Calendar lane assignment
# --------------------------------------------------------------------------

def assign_lanes(courses):
    """Side-by-side placement for meetings that overlap on the same day.

    Greedy interval-graph coloring per (semester, day): every meeting gets a
    `lane`, and every meeting in an overlapping cluster shares a `lanes` count
    so the template can size the blocks as a fraction of the column.
    """
    buckets = {}
    for course in courses:
        for meeting in course["meetings"]:
            buckets.setdefault((course["semester"], meeting["day_index"]), []).append(meeting)

    for meetings in buckets.values():
        meetings.sort(key=lambda m: (m["start_minutes"], m["end_minutes"]))
        cluster, cluster_end = [], None
        for meeting in meetings:
            # A gap with no overlap ends the cluster and resets the lane count.
            if cluster_end is not None and meeting["start_minutes"] >= cluster_end:
                _finalize(cluster)
                cluster, cluster_end = [], None
            lane = 0
            used = {m["lane"] for m in cluster if m["end_minutes"] > meeting["start_minutes"]}
            while lane in used:
                lane += 1
            meeting["lane"] = lane
            cluster.append(meeting)
            cluster_end = max(cluster_end or 0, meeting["end_minutes"])
        _finalize(cluster)


def _finalize(cluster):
    if not cluster:
        return
    lanes = max(m["lane"] for m in cluster) + 1
    for meeting in cluster:
        meeting["lanes"] = lanes


# --------------------------------------------------------------------------
# University colors
# --------------------------------------------------------------------------

def read_universities():
    """Parse `_data/universities.yml` into {slug: {key: value}}.

    Deliberately a tiny hand-rolled reader for the flat two-level shape we
    write, so the script stays stdlib-only and needs no pip install in CI.
    """
    universities, current = {}, None
    if not os.path.exists(UNIVERSITIES_YML):
        return universities
    for line in open(UNIVERSITIES_YML, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            current = line.split(":", 1)[0].strip()
            universities[current] = {}
        elif current and ":" in line:
            key, value = line.strip().split(":", 1)
            universities[current][key.strip()] = value.strip().strip('"')
    return universities


def append_universities(unknown, universities):
    """Add newly-seen universities with a placeholder color.

    A school that shows up in the form should never break the calendar, so we
    give it a distinct fallback color immediately and flag it for a real one.
    """
    with open(UNIVERSITIES_YML, "a", encoding="utf-8") as handle:
        for i, (slug, name) in enumerate(sorted(unknown.items())):
            color = FALLBACK_COLORS[(len(universities) + i) % len(FALLBACK_COLORS)]
            handle.write(
                f"\n{slug}:\n"
                f"  name: {yaml_str(name)}\n"
                f"  abbr: {yaml_str(slug)}\n"
                f"  color: {yaml_str(color)} # TODO: replace with this school's brand color\n"
            )


# --------------------------------------------------------------------------
# Emitting the collection
# --------------------------------------------------------------------------

def yaml_str(value: str) -> str:
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "course"


def is_url(value: str) -> bool:
    """The link column is free text -- two rows say 'Still working on that....'"""
    return bool(value) and re.match(r"^https?://\S+$", value.strip()) is not None


def render(course) -> str:
    lines = ["---", "layout: course"]
    lines.append(f"title: {yaml_str(course['title'])}")
    lines.append(f"permalink: {course['permalink']}")
    lines.append(f"course_number: {yaml_str(course['course_number'])}")
    lines.append(f"university: {yaml_str(course['university'])}")
    lines.append(f"university_slug: {yaml_str(course['university_slug'])}")
    if course["instructor"]:
        lines.append(f"instructor: {yaml_str(course['instructor'])}")
    lines.append(f"semester: {yaml_str(course['semester'])}")
    lines.append(f"semester_order: {course['semester_order']}")
    if course["link"]:
        lines.append(f"link: {yaml_str(course['link'])}")
    if course["meeting_times"]:
        lines.append(f"meeting_times: {yaml_str(course['meeting_times'])}")

    if course["meetings"]:
        lines.append("meetings:")
        for meeting in sorted(course["meetings"], key=lambda m: (m["day_index"], m["start_minutes"])):
            lines.append(f"  - day_index: {meeting['day_index']}")
            lines.append(f"    day_name: {yaml_str(meeting['day_name'])}")
            lines.append(f"    day_abbr: {yaml_str(meeting['day_abbr'])}")
            lines.append(f"    start: {yaml_str(meeting['start'])}")
            lines.append(f"    end: {yaml_str(meeting['end'])}")
            lines.append(f"    start_minutes: {meeting['start_minutes']}")
            lines.append(f"    end_minutes: {meeting['end_minutes']}")
            lines.append(f"    lane: {meeting.get('lane', 0)}")
            lines.append(f"    lanes: {meeting.get('lanes', 1)}")
            if meeting["label"]:
                lines.append(f"    label: {yaml_str(meeting['label'])}")
    if course["unparsed"]:
        lines.append("unscheduled:")
        for segment in course["unparsed"]:
            lines.append(f"  - {yaml_str(segment)}")

    lines.append("---")
    lines.append("")
    lines.append(course["description"].strip() if course["description"] else "_No description submitted._")
    lines.append("")
    return "\n".join(lines)


def build_courses(rows, universities):
    courses, unknown, seen = [], {}, set()

    for row in rows:
        get = lambda key: (row.get(key) or "").strip()
        title = get("Course Name")
        university = get("University Name")
        if not title or not university:
            continue

        uni_slug = slugify(university)
        entry = universities.get(uni_slug)
        if not entry:
            unknown[uni_slug] = university

        semester = get("Semester") or "Unscheduled"
        raw_times = get("Meeting Times")
        meetings, unparsed = parse_meetings(raw_times)
        link = get("Link to Syllabus or Course Website")
        number = get("Course Number")

        abbr = (entry or {}).get("abbr") or uni_slug
        base = slugify(f"{abbr}-{number or title}")
        slug = base
        suffix = 2
        while (semester, slug) in seen:
            slug = f"{base}-{suffix}"
            suffix += 1
        seen.add((semester, slug))

        order = SEMESTER_ORDER.index(semester) + 1 if semester in SEMESTER_ORDER else 99
        courses.append(
            {
                "title": title,
                "course_number": number,
                "university": university,
                "university_slug": uni_slug,
                "instructor": get("Instructor Name"),
                "semester": semester,
                "semester_order": order,
                "semester_slug": slugify(semester),
                "description": get("Course Description"),
                "link": link if is_url(link) else "",
                "meeting_times": raw_times,
                "meetings": meetings,
                "unparsed": unparsed,
                "slug": slug,
                "permalink": f"/courses/{slugify(semester)}/{slug}/",
            }
        )

    assign_lanes(courses)
    return courses, unknown


def write_collection(courses, check_only=False):
    """Rewrite `_courses/` from scratch so deleted form rows disappear too."""
    files = {
        os.path.join(COURSES_DIR, c["semester_slug"], f"{c['slug']}.md"): render(c)
        for c in courses
    }

    existing = {}
    for dirpath, _, filenames in os.walk(COURSES_DIR):
        for name in filenames:
            if name.endswith(".md"):
                path = os.path.join(dirpath, name)
                existing[path] = open(path, encoding="utf-8").read()

    if existing == files:
        return False
    if check_only:
        return True

    if os.path.isdir(COURSES_DIR):
        shutil.rmtree(COURSES_DIR)
    for path, content in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if regeneration would change files")
    parser.add_argument("--csv", help="read a local CSV instead of fetching the sheet")
    args = parser.parse_args()

    if args.csv:
        text = open(args.csv, encoding="utf-8").read()
    else:
        request = urllib.request.Request(CSV_URL, headers={"User-Agent": "nyc-psychometrics-course-sync"})
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8")

    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        sys.exit("error: sheet returned no rows; refusing to wipe _courses/")

    universities = read_universities()
    courses, unknown = build_courses(rows, universities)
    if not courses:
        sys.exit("error: no usable course rows; refusing to wipe _courses/")

    if unknown and not args.check:
        append_universities(unknown, universities)

    changed = write_collection(courses, check_only=args.check)

    scheduled = sum(1 for c in courses if c["meetings"])
    print(f"{len(courses)} courses ({scheduled} placed on a calendar) across {len({c['semester'] for c in courses})} semesters")
    for course in courses:
        if course["unparsed"]:
            print(f"  ! unreadable meeting time: {course['title']} -- {course['unparsed']}")
    for slug, name in sorted(unknown.items()):
        print(f"  ! new university '{name}' added to _data/universities.yml with a placeholder color")

    if args.check and changed:
        sys.exit("_courses/ is out of date; run: python3 bin/fetch_courses.py")
    print("up to date" if not changed else "wrote _courses/")


if __name__ == "__main__":
    main()
