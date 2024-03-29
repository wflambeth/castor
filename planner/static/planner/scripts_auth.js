"use strict";

/* 
Scripts for auth-only functions (creating/saving/deleting schedules, updating schedule names)
*/

function createSchedule() {
    /* Creates a new schedule on request, then redirects to that schedule's page. */
    const request = new Request(
        "/schedules",
        {headers: {'X-CSRFToken': csrftoken,
                     'Accept': 'application/json'},
            method: 'POST',
            mode: 'same-origin'
        });

    fetch(request)
        .then((response) => {
            // raise error if response code is not 2XX
            if (response.ok) return response.json();
            return response.json().then(response => {throw new Error(response.error)})})
        .then((data) => {
            // redirect to new schedule
            window.open("/schedules/" + data.schedule, "_self");
        })
        .catch((error) => {
            // log error if schedule creation fails
            console.error('Error creating schedule: ', error);
        });
}

let create_btn = document.getElementById('create-sched');
if (create_btn !== null) { // (e.g. if max schedules not reached)
    create_btn.addEventListener('click', createSchedule);    
}

function saveSchedule() {
    /* Saves any pending changes to the course schedule (dates, scheduled courses), by 
       JSON-encoding the state object and sending to server PATCH endpoint. */
    const request = new Request(
        "/schedules" + '/' + page_sched_id,
        {headers: {'X-CSRFToken': csrftoken,
                   'Content-Type': 'application/json'}, 
         body: JSON.stringify(changes),
         method: 'PATCH',
         mode: 'same-origin'
    });
    
    fetch(request)
        .then((response) => {
            // raise error if response code is not 2XX
            if (response.ok) return response.json();
            return response.json().then(response => {throw new Error(response.error)})})
        .then((data) => {
            // report success. TODO: make this visible in UI
            console.log('Saved: ', data);

            // clear state object after saving
            changes.courses = {}; 
            changes.dates.start = {qtr: null, year: null};
            changes.dates.end = {qtr: null, year: null};
        })
        .catch((error) => {
            console.error('Error saving schedule: ', error);
        });
}

let saveBtn = document.getElementById('submit-button');
saveBtn.addEventListener("click", saveSchedule);

/* Delete existing schedules via sidebar menu. */
function delete_schedule(event) {
    event.preventDefault();
    const id = event.target.getAttribute('data-delete-id');
    const request = new Request(
        "/schedules" + '/' + id,
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

                // if there were previously 10 schedules, show create button again
                if (document.getElementsByClassName('delete-sched').length == 9) {
                    document.getElementById('create-sched').hidden = false;
                }
            }
        })
        .catch((error) => {
            console.error('Error deleting schedule: ', error);
        });
}

const delete_btns = Object.values(document.getElementsByClassName('delete-sched'));
delete_btns.forEach(btn => {
    btn.addEventListener('click', delete_schedule);
});

/* Control visibility for update-title form elements  */
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