---
# ---------------------------------------------------------------------------
# EVENT TEMPLATE -- not published; _templates/ is excluded from the build.
#
# To add an event:
#   1. Copy this file to _events/YYYY-MM-DD-short-slug.md
#      The filename sets the URL, e.g. /events/2027-03-14-spring-social/
#   2. Fill in the fields below and delete the ones you do not need.
#   3. Delete these comment lines.
#
# `layout: event` is applied automatically by the collection default in
# _config.yml -- do not set it here.
# ---------------------------------------------------------------------------

# Required. Shown as the page heading and as the link text on the events page.
title: Event title here

# Required. When the event starts, including the timezone offset
# (-0500 in winter / EST, -0400 in summer / EDT).
# Future dates are fine: `future: true` in _config.yml builds them.
date: 2027-03-14 17:00:00-0400

# Optional. When it ends. Same day renders as "5:00-7:00 pm"; a later day
# renders as a date range, so multi-day conferences work too.
end_date: 2027-03-14 19:00:00-0400

# Optional. Free text, shown under "Where".
location: Room and address

# Optional. Shown as a subtitle under the title.
speaker: Speaker Name

# Optional. Registration or conference page, shown under "More info".
link: https://example.org/

# `false` gives the event its own page, linked from the events list.
# `true` renders the body inline in the list instead, with no page of its own --
# use it for short announcements that have nowhere to link to.
inline: false

related_posts: false
---

The body of the event, in Markdown. A short paragraph on what the event is and
who it is for. **Bold** and [links](https://example.org/) both work.

Leave out details that are already in the front matter above -- the date,
location, and link are rendered from those fields.
