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

const qtr_map = {
    '0' : 'Winter',
    '1' : 'Spring',
    '2' : 'Summer', 
    '3' : 'Fall'
}

const add_qtr_before = document.getElementById('add_qtr_before');
const add_qtr_after = document.getElementById('add_qtr_after');
let schedule_wrapper = document.getElementById('schedule-wrapper');
let qtr_nodes = schedule_wrapper.childNodes;

// TODO: make an empty node here, that we can just make copies of as needed
function new_quarter(yr, qtr) {
    let parent = document.createElement('div');
    parent.setAttribute('class', 'qtr grid');
    parent.setAttribute('id', '_' + yr + '_' + qtr);
    parent.setAttribute('data-yr', yr);
    parent.setAttribute('data-qtr', qtr);

    let title = document.createElement('div');
    title.setAttribute('class', 'term-title');
    title.innerHTML = qtr_map[qtr] + ' ' + yr;

    let container = document.createElement('div');
    container.setAttribute('class', 'course-container');
    //TODO: Can I remove these two from child div now that they're in parent? 
    container.setAttribute('data-yr', yr);
    container.setAttribute('data-qtr', qtr);

    let placeholder = document.createElement('div');
    placeholder.setAttribute('class', 'course-item empty-item');
    let empty_title = document.createElement('span');
    empty_title.setAttribute('class', 'empty-title course-title');
    empty_title.innerHTML = 'temp placeholder: empty term';
    placeholder.appendChild(empty_title);

    parent.appendChild(title);
    parent.appendChild(container);
    container.appendChild(placeholder);

    return parent;
}

add_qtr_before.addEventListener("click", (event) => {
    // qtr_nodes declared above; live list of children of sched wrapper
    let topnode = qtr_nodes[3];
    let yr = topnode.getAttribute('data-yr');
    let qtr = topnode.getAttribute('data-qtr');

    // Transform data attributes 
    if (qtr > 0) {
        qtr -= 1;
    } else {
        yr -= 1;
        qtr = 3;
    }

    // create new node and append at proper place
    let newtop = new_quarter(yr, qtr);
    schedule_wrapper.insertBefore(newtop, topnode);

    // TODO: use this space to modify data POSTed to server
});

add_qtr_after.addEventListener("click", (event) => {
    let bottomnode = qtr_nodes[(qtr_nodes.length - 4)];
    let yr = +bottomnode.getAttribute('data-yr');
    let qtr = +bottomnode.getAttribute('data-qtr');

    if (qtr > 2){
        qtr = 0;
        yr = (yr + 1).toString();
    } else {
        qtr = (qtr + 1).toString();
    }
    let newbottom = new_quarter(yr, qtr);
    schedule_wrapper.insertBefore(newbottom, bottomnode.nextSibling);
});


/* CSRF token for fetch authentication */
const csrftoken = Cookies.get('csrftoken');