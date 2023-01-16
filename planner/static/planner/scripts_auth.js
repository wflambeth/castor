"use strict";

/* Save scheduled course updates as logged by dropLogger function (in scripts_base.js) */
function saveSchedule() {
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
        console.log('Success: ', data);
    })
    .catch((error) => {
        console.log('Error:', error);
    });
}
let saveBtn = document.getElementById('submit-button');
saveBtn.addEventListener("click", saveSchedule);

/* Edit and save schedule titles
function updateTitle(text) {
    const request = new Request(
        paths.update_title,
        {headers: 
            {'X-CSRFToken': csrftoken,
             'Content-Type': 'application/json'}, 
         body: JSON.stringify({
            'schedule': page_sched_id,
            'title': text
        }),
        method: 'POST',
        mode: 'same-origin'
    });

    fetch(request)
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
 */
/* Delete existing schedules */
function delete_schedule(event) {
    event.preventDefault();
    const id = event.target.getAttribute('data-delete-id');
    const request = new Request(
        paths.delete + "?id=" + id,
        {headers: 
            {'X-CSRFToken': csrftoken,
             'Content-Type': 'application/json'},
        method: 'DELETE',
        mode: 'same-origin'
    });

    fetch(request)
        .then(function (response) {
            if (response.status === 204) {
                document.getElementById(id + '_parent').remove();
                return 'Schedule ' + id + ' deleted';
            } else { return Promise.reject(response); }
        })
        .then(function (msg) {
            console.log(msg);
        })
        .catch(function (err) {
            console.error(err);
        });
}
const delete_btns = Object.values(document.getElementsByClassName('delete-sched'));
delete_btns.forEach(btn => {
    btn.addEventListener('click', delete_schedule);
});

/* CSRF token for fetch authentication */
const csrftoken = Cookies.get('csrftoken');