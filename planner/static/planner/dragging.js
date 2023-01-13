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
      paths.save,
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

  let saveBtn = document.getElementById('submit-button');
  saveBtn.addEventListener("click", saveSchedule);

  function updateTitle(text) {

    const title_POST_info = {
      'schedule': page_sched_id,
      'title': text
    }

    const request = new Request(
      paths.update_title,
      {headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },body: JSON.stringify(title_POST_info),
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
    })
  };
  
  let editing = false;
  let title = document.getElementById('sched-name');
  let titleEditLink = document.getElementById('edit-title');
  titleEditLink.addEventListener("click", (event) => {
    event.preventDefault();
    if (editing === false) {
      title.setAttribute('contentEditable', 'true');
      title.focus();

      // Selects all text in the title, shoutout StackOverflow:
      // https://stackoverflow.com/questions/6139107/programmatically-select-text-in-a-contenteditable-html-element
      // TODO: this looks terrible, breaks header (could just use a popup instead)?
      let range = document.createRange();
      range.selectNodeContents(title);
      let sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);

      titleEditLink.textContent = '(save)'
      editing = true;
    } else {
      title.setAttribute('contentEditable', 'false');
      titleEditLink.textContent = '(edit)'
      editing = false;
      updateTitle(title.innerText);
    }
  });

  // DELETE handler for our buttons
  // TODO: how to handle if someone wants to delete currently active schedule 
  //    (disabled for now)
  function delete_schedule(event) {
    event.preventDefault();
    const id = event.target.getAttribute('data-delete-id');
    const req = new Request(
      paths.delete + "?id=" + id,
      {
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        },
        method: 'DELETE'
      });

    fetch(req, {method: 'DELETE', mode:'same-origin'})
      .then(function (response){
        if (response.status === 204){
          document.getElementById(id + '_parent').remove();
          return 'Schedule ' + id + ' deleted';
        } else {return Promise.reject(response);}
      }).then(function(data){
          console.log(data);
      }).catch(function(err){
        console.log(err);
      });
  }
  
  const delete_btns = Object.values(document.getElementsByClassName('delete-sched'));
  delete_btns.forEach(btn => {
    btn.addEventListener('click', delete_schedule);
  });
}

const POST_changes = {s: page_sched_id, courses: {}};
const csrftoken = Cookies.get('csrftoken');