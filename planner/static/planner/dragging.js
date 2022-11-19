"use strict";

var drake = dragula({
    isContainer: function (el) {
      return el.classList.contains('course-container');
    }
  });

drake.on('drop', dropLogger);

function dropLogger(el, target, source, sibling) {
  if (target !== source) {
    let id = el.getAttribute('data-id');
    let year = target.getAttribute('data-yr');
    let qtr = target.getAttribute('data-qtr');
    console.log(id, year, qtr);
    POST_changes.courses[id] = {year, qtr}
  }
}

function saveSchedule() {
  console.log(page_sched_id);
  fetch('http://127.0.0.1:8000/csp/save', {
    method: 'POST', 
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(POST_changes),
  })
  .then((response) => response.json())
  .then((data) => {
    console.log('Success: ', data);
  })
  .catch((error) => {
    console.log('Error:', error);
  });
}

let btn = document.getElementById('submit-button');
btn.addEventListener("click", saveSchedule);

let POST_changes = {s: page_sched_id, courses: {}}