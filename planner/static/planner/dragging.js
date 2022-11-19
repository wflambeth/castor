var drake = dragula({
    isContainer: function (el) {
      return el.classList.contains('course-container');
    }
  });

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

// next step: add drop events to include info here
// store course and updated info
let POST_changes = {id: page_sched_id, courses: {}}