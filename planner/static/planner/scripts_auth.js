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
            // clear save object
            POST_changes.courses = {};
            POST_changes.dates.start = {qtr: null, year: null};
            POST_changes.dates.end = {qtr: null, year: null};
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

/* Expand existing schedules by semester */
const qtr_map = {
    '0': 'Winter',
    '1': 'Spring',
    '2': 'Summer',
    '3': 'Fall'
}
const add_qtr_before = document.getElementById('add_qtr_before');
const add_qtr_after = document.getElementById('add_qtr_after');
let schedule_wrapper = document.getElementById('schedule-wrapper');
let qtr_nodes = schedule_wrapper.children;

function new_quarter(yr, qtr) {
    let parent = document.createElement('div');
    parent.setAttribute('class', 'qtr grid');
    parent.setAttribute('id', '_' + yr + '_' + qtr);
    parent.setAttribute('data-yr', yr);
    parent.setAttribute('data-qtr', qtr);

    let title = document.createElement('div');
    title.setAttribute('class', 'term-title');
    title.innerHTML = qtr_map[qtr] + ' ' + yr + ' ';
    let delete_link = document.createElement('a');
    delete_link.setAttribute('href', '#');
    delete_link.setAttribute('class', 'delete-term');
    delete_link.setAttribute('data-delete-yr', yr);
    delete_link.setAttribute('data-delete-qtr', qtr);
    delete_link.innerText = "[x]";
    delete_link.addEventListener('click', update_qtrs);
    
    let container = document.createElement('div');
    container.setAttribute('class', 'course-container');
    //TODO: Can I remove these two from child div now that they're in parent? 
    container.setAttribute('data-yr', yr);
    container.setAttribute('data-qtr', qtr);

    let placeholder = document.createElement('div');
    placeholder.setAttribute('class', 'course-item empty-item placeholder');
    let empty_title = document.createElement('span');
    empty_title.setAttribute('class', 'empty-title course-title');
    empty_title.innerHTML = 'placeholder: empty term';
    placeholder.appendChild(empty_title);

    title.appendChild(delete_link);
    parent.appendChild(title);
    parent.appendChild(container);
    container.appendChild(placeholder);

    return parent;
}

add_qtr_before.addEventListener("click", (event) => {
    // qtr_nodes declared above; live list of children of sched wrapper
    let topnode = qtr_nodes[1];
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
    topnode.children[0].children[0].hidden = true;
    schedule_wrapper.insertBefore(newtop, topnode);

    POST_changes.dates.start.year = yr;
    POST_changes.dates.start.qtr = qtr;
    console.log(POST_changes);
});

add_qtr_after.addEventListener("click", (event) => {
    let bottomnode = qtr_nodes[(qtr_nodes.length - 2)];
    let yr = +bottomnode.getAttribute('data-yr');
    let qtr = +bottomnode.getAttribute('data-qtr');

    if (qtr > 2) {
        qtr = 0;
        yr = (yr + 1).toString();
    } else {
        qtr = (qtr + 1).toString();
    }
    let newbottom = new_quarter(yr, qtr);
    bottomnode.children[0].children[0].hidden = true;
    schedule_wrapper.insertBefore(newbottom, bottomnode.nextSibling);

    POST_changes.dates.end.year = yr;
    POST_changes.dates.end.qtr = qtr;
});

/* CSRF token for fetch authentication */
const csrftoken = Cookies.get('csrftoken');

// hide delete button 
// TODO: why am I using window.onload here, better way to structure this? 
window.onload = (event) => {    
    // add event listeners 
    for (var i = 1; i < qtr_nodes.length - 1; ++i) {
        qtr_nodes[i].children[0].children[0].addEventListener('click', update_qtrs);
    }
    // ensure first & last qtrs are deletable
    qtr_nodes[1].children[0].children[0].hidden = false;
    qtr_nodes[qtr_nodes.length - 2].children[0].children[0].hidden = false;
}

function update_qtrs (event) {
    event.preventDefault();
    // get course container
    const course_container = event.target.parentNode.nextElementSibling;
    if (course_container.children[0].classList.contains('placeholder')) {
        // wipe empty node off the face of the earth
        
        event.target.parentNode.parentNode.remove();
        // get first and last from qtr_nodes
        let first = qtr_nodes[1];
        let last = qtr_nodes[qtr_nodes.length - 2];

        // set their [x]es visible
        first.children[0].children[0].hidden = false;
        first.children[0].children[0].addEventListener('click', update_qtrs);
        last.children[0].children[0].hidden = false;
        last.children[0].children[0].addEventListener('click', update_qtrs);

        // update POST_changes with needed info
        POST_changes.dates.start.year = first.getAttribute('data-yr');
        POST_changes.dates.start.qtr = first.getAttribute('data-qtr');

        POST_changes.dates.end.year = last.getAttribute('data-yr');
        POST_changes.dates.end.qtr = last.getAttribute('data-qtr');
    } else {
        // remove existing classes from non-empty node
        const req_container = document.getElementById('req-container');
        const elec_container = document.getElementById('elec-container');

        while (course_container.children.length > 0) {
            let crs = course_container.children[0];
            // move scheduled course to appropriate container
            if (crs.getAttribute('data-req') === 'true'){
                req_container.insertBefore(crs, req_container.children[0]);
            } else {
                elec_container.insertBefore(crs, elec_container.children[0]);
            }
            // update changes to be saved and index for dragging validation
            let crs_id = crs.getAttribute('data-id');
            POST_changes.courses[crs_id] = {year: null, qtr: null};
            crs_idx[crs_id] = -1;
        }
        let placeholder = new_placeholder();
        course_container.append(placeholder);
        // check if qtr is first/last in list, and hide the x if not
        if (!(course_container.parentNode === qtr_nodes[1]) && 
            !(course_container.parentNode === qtr_nodes[qtr_nodes.length - 2])){
                event.target.hidden = true;
            }
    }
}

function new_placeholder() {
    let placeholder = document.createElement('div');
    placeholder.setAttribute('class', 'course-item empty-item placeholder');
    let empty_title = document.createElement('span');
    empty_title.setAttribute('class', 'empty-title course-title');
    empty_title.innerHTML = 'placeholder: empty term';
    placeholder.appendChild(empty_title);

    return placeholder
}

/* Set initial indices of crs_idx (for drag validation logic) */
const starting_nodes = Array.from(qtr_nodes);
for (var i = 1; i < starting_nodes.length - 1; ++i) {
    let nodes = starting_nodes[i].children[1].children;
    for (var node of nodes) {
        if (node.classList.contains('course')) {
            crs_idx[node.getAttribute('data-id')] = i;
        }
    }
}