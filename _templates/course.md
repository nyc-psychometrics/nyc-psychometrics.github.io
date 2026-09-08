---
# ---------------------------------------------------------------------------
# COURSE TEMPLATE -- not published; _templates/ is excluded from the build.
#
# To add a course:
#   1. Copy this file to _courses/<semester>/<slug>.md
#      e.g. _courses/fall/columbia-hudm-5123.md
#   2. Fill in the fields below.
#   3. Delete these comment lines.
#
# The filename is up to you; `permalink` below is what sets the URL, so keep
# the two consistent.
#
# If the university is new, add it to _data/universities.yml first so its
# calendar blocks get the right brand color.
# ---------------------------------------------------------------------------

layout: course

# Required. Course title, without the course number.
title: Course Title Here

# Required. Must be unique, and must match the file's location.
permalink: /courses/fall/university-abbr-course-number/

course_number: DEPT 1234
university: University Name

# Required. Must match a key in _data/universities.yml -- this is what selects
# the color used on the calendar.
university_slug: university-name

instructor: Instructor Name

# "Fall" or "Spring". semester_order sets the order of sections on the courses
# page: Fall is 1, Spring is 2.
semester: Fall
semester_order: 1

# Optional. Syllabus or course page. Must be a real URL or leave it out.
link: https://example.edu/course

# Optional. The meeting time as a human would write it. Shown verbatim on the
# course page under "As submitted".
meeting_times: Tu 4:15-6:15pm

# Optional, but needed for the course to appear on the week calendar.
# Add one entry per weekly meeting; a course with a separate lab gets two.
#   day_index:      0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
#   start/end:      display text
#   *_minutes:      minutes past midnight -- this is what positions the block
#                   (4:15pm = 16*60+15 = 975)
#   lane/lanes:     side-by-side placement for courses that overlap on the same
#                   day. Leave as lane 0 / lanes 1 when nothing overlaps. When
#                   two courses do overlap, give BOTH lanes: 2, and set lane: 0
#                   on one and lane: 1 on the other, or they will sit on top of
#                   each other.
#   label:          optional, e.g. Lab or Lecture
meetings:
  - day_index: 1
    day_name: Tuesday
    day_abbr: Tue
    start: 4:15pm
    end: 6:15pm
    start_minutes: 975
    end_minutes: 1095
    lane: 0
    lanes: 1
---

The course description, in Markdown. This is the body of the course page.
