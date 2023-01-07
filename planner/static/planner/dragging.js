"use strict";
// if (auth) {} # use this pattern for determining if we're saving to an existing schedule, or building a new one 
// could have separate dropLogger_auth and dropLogger_demo functions
// don't need a saveSchedule because we'll be passing the context along to the login page, then back to the render page 

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
    POST_changes.courses[id] = {year, qtr};
  }
}

// Only need this if user is logged in - otherwise, not saving schedule 
if (auth) {
  function saveSchedule() {
    const request = new Request(
      'http://127.0.0.1:8000/csp/save',
      {headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },body: JSON.stringify(POST_changes),
    method: 'POST'}
    );
    fetch(request, {
      method: 'POST', 
      mode: 'same-origin'})
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
}

const POST_changes = {s: page_sched_id, courses: {}};
const csrftoken = Cookies.get('csrftoken');