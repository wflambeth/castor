"use strict";

/* 
Scripts for auth-only functions (saving/deleting schedules, updating schedule names)
*/

function saveSchedule() {
    /* Saves any pending changes to the course schedule (dates, scheduled courses), by 
       JSON-encoding the state object and sending to server POST endpoint. */
    const request = new Request(
        paths.save,
        {headers: {'X-CSRFToken': csrftoken,
                   'Content-Type': 'application/json'}, 
         body: JSON.stringify(POST_changes),
         method: 'POST',
         mode: 'same-origin'
    });
    
    fetch(request)
        .then((response) => response.json())
        .then((data) => {
            // clear state object after successful save
            POST_changes.courses = {}; 
            POST_changes.dates.start = {qtr: null, year: null};
            POST_changes.dates.end = {qtr: null, year: null};
            // report success. TODO: make this visible in UI
            console.log('Success: ', data);
        })
        .catch((error) => {
            console.log('Error:', error);
        });
}
let saveBtn = document.getElementById('submit-button');
saveBtn.addEventListener("click", saveSchedule);

/* Delete existing schedules, if requested via sidebar menu. */
function delete_schedule(event) {
    event.preventDefault();
    const id = event.target.getAttribute('data-delete-id');
    const request = new Request(
        "/schedule" + '/' + id,
        {headers: 
            {'X-CSRFToken': csrftoken,
             'Content-Type': 'application/json'},
        method: 'DELETE',
        mode: 'same-origin'
    });

    fetch(request)
        .then(function (response) {
            if (response.status === 204) {
                return 'Schedule ' + id + ' deleted';
            } else { return Promise.reject(response); }
        })
        .then(function (msg) {
            // log that schedule was deleted
            console.log(msg);
            if (page_sched_id == id) {
                // if current schedule was deleted, load most recently created
                window.open("/", "_self");
            } else {
                // otherwise, remove schedule from sidebar
                document.getElementById(id + '_parent').remove();
            }
        })
        .catch(function (err) {
            console.error(err);
        });
}
const delete_btns = Object.values(document.getElementsByClassName('delete-sched'));
delete_btns.forEach(btn => {
    btn.addEventListener('click', delete_schedule);
});

/* Update schedule titles  */
let edit_btn = document.getElementById('title-edit');
let cancel_btn = document.getElementById('cancel-edit');
let title_span = document.getElementById('title-span');

edit_btn.addEventListener('click', () => {
    edit_btn.hidden = true;
    title_span.hidden = false;
});

cancel_btn.addEventListener('click', () => {
    title_span.hidden = true;
    edit_btn.hidden = false;
});

/* CSRF token for fetch authentication */
const csrftoken = Cookies.get('csrftoken');