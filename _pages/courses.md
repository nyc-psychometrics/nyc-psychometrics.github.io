---
layout: page
title: courses
permalink: /courses/
description: Graduate courses in psychometrics, measurement, and quantitative methods offered across New York City.
nav: true
nav_order: 2
---

Courses submitted by faculty across the city, grouped by semester. Each calendar shows
when that semester's courses meet, color-coded by university. Click any course for its
description, meeting times, and syllabus link.

{% assign ordered = site.courses | sort: "semester_order" | map: "semester" | uniq %}

{% if ordered.size == 0 %}

_No courses have been submitted yet._

{% else %}
{% for semester in ordered %}
{% assign semester_courses = site.courses | where: "semester", semester | sort: "course_number" %}

<h2 id="{{ semester | slugify }}" class="course-semester">{{ semester }}</h2>

{% include course_calendar.liquid courses=semester_courses semester=semester %}

<div class="table-responsive">
  <table class="table table-sm course-table">
    <thead>
      <tr>
        <th scope="col">Course</th>
        <th scope="col">Number</th>
        <th scope="col">University</th>
        <th scope="col">Instructor</th>
      </tr>
    </thead>
    <tbody>
      {% for course in semester_courses %}
        {% assign uni = site.data.universities[course.university_slug] %}
        <tr>
          <td>
            <a href="{{ course.url | relative_url }}">{{ course.title }}</a>
          </td>
          <td class="course-table-number">{{ course.course_number }}</td>
          <td>
            <span
              class="course-uni-dot"
              style="--uni-color: {% if uni.color %}{{ uni.color }}{% else %}var(--global-theme-color){% endif %}"
              aria-hidden="true"
            ></span>
            {{ course.university }}
          </td>
          <td>{{ course.instructor }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{% endfor %}
{% endif %}

<p class="course-footnote">
  Teaching a relevant course? Share it on the
  <a href="https://groups.google.com/g/psychometrics-nyc">Google Group</a> and it will be added here.
</p>
