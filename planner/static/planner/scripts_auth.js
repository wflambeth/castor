"use strict";

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

/* Edit and save schedule titles. TODO: Currently disabled due to jank, coming soon. 
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

/* Delete existing schedules, if requested via sidebar menu. */
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
                // removes item from DOM if removal is successful
                document.getElementById(id + '_parent').remove();
                return 'Schedule ' + id + ' deleted';
            } else { return Promise.reject(response); }
        })
        .then(function (msg) {
            // TODO: add messaging for successful/errored deletion
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

/* Allows new quarters to be added to schedule. */
// For iterative title generation
const qtr_map = {
    '0': 'Winter',
    '1': 'Spring',
    '2': 'Summer',
    '3': 'Fall'
}
let schedule_wrapper = document.getElementById('schedule-wrapper');
let qtr_nodes = schedule_wrapper.children;

function new_quarter(yr, qtr) {
    /*
     Generates new quarter DOM elements as needed. 
    */
    // parent div, sets appropriate attributes
    let parent = document.createElement('div');
    parent.setAttribute('class', 'qtr grid');
    parent.setAttribute('id', '_' + yr + '_' + qtr);
    parent.setAttribute('data-yr', yr);
    parent.setAttribute('data-qtr', qtr);

    // title div, including quarter-delete link 
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
    
    // actual course container/droppable area
    let container = document.createElement('div');
    container.setAttribute('class', 'course-container');
    //TODO: Can I remove these two from child div now that they're in parent? 
    container.setAttribute('data-yr', yr);
    container.setAttribute('data-qtr', qtr);

    let placeholder = new_placeholder()

    title.appendChild(delete_link);
    parent.appendChild(title);
    parent.appendChild(container);
    container.appendChild(placeholder);

    return parent;
}

// Add new quarter to top/beginning of schedule
document.getElementById('add_qtr_before').addEventListener("click", (event) => {
    // get current top node
    let topnode = qtr_nodes[1];
    let yr = topnode.getAttribute('data-yr');
    let qtr = topnode.getAttribute('data-qtr');

    // Iterate data attributes for new qtr
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

    // Update schedule bounds to be saved to DB
    POST_changes.dates.start.year = yr;
    POST_changes.dates.start.qtr = qtr;

    // Increment course indices
    for (const [key, value] of Object.entries(crs_idx)){
        if (value !== -1) {
            crs_idx[key] += 1;
        }
    }
});

// Add new quarter to bottom/end of schedule
document.getElementById('add_qtr_after').addEventListener("click", (event) => {
    // get current bottom node
    let bottomnode = qtr_nodes[(qtr_nodes.length - 2)];
    let yr = +bottomnode.getAttribute('data-yr');
    let qtr = +bottomnode.getAttribute('data-qtr');

    // Iterate data attributes for new qtr
    if (qtr > 2) {
        qtr = 0;
        yr = (yr + 1).toString();
    } else {
        qtr = (qtr + 1).toString();
    }
    // create new node and append at proper place
    let newbottom = new_quarter(yr, qtr);
    bottomnode.children[0].children[0].hidden = true;
    schedule_wrapper.insertBefore(newbottom, bottomnode.nextSibling);

    // Update schedule bounds to be saved to DB
    POST_changes.dates.end.year = yr;
    POST_changes.dates.end.qtr = qtr;
});

// hide delete buttons for non-empty and non-edge terms 
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

// This function is called when hitting the [x] on a quarter (TODO: needs a better name)
// Clears qtrs with courses within them, and is also used to delete qtrs on the edges
function update_qtrs (event) {
    event.preventDefault();
    // get course container
    const course_container = event.target.parentNode.nextElementSibling;
    if (course_container.children[0].classList.contains('placeholder')) {
        /* If container is empty (i.e. has placeholder), we delete it and update the
           schedule's bounds in the DOM and DB.  
           Separate/parallel flows for deleting first and last items; no others
           can be deleted entirely. 
           */
        // if node being deleted is the *first* in our list
        if (qtr_nodes[1].children[1] === course_container) {
            // kick things off by nuking said element
            event.target.parentNode.parentNode.remove();

            // get new first from qtr_nodes, set [x] visible
            let first = qtr_nodes[1];
            first.children[0].children[0].hidden = false;
            // pretty sure I don't need these? first.children[0].children[0].addEventListener('click', update_qtrs);

            // update save state with new bounds
            POST_changes.dates.start.year = first.getAttribute('data-yr');
            POST_changes.dates.start.qtr = first.getAttribute('data-qtr');

            // Decrement course indices
            for (const [key, value] of Object.entries(crs_idx)){
                if (value !== -1) {
                    crs_idx[key] -= 1;
                }
            }
            console.log(crs_idx);

        } else if (qtr_nodes[qtr_nodes.length - 2].children[1] === course_container) {
            // still kick things off by nuking said element
            event.target.parentNode.parentNode.remove();

            // get new last from qtr_nodes, set [x] visible
            let last = qtr_nodes[qtr_nodes.length - 2];
            last.children[0].children[0].hidden = false;
            //last.children[0].children[0].addEventListener('click', update_qtrs);

            // update save state with new bounds
            POST_changes.dates.end.year = last.getAttribute('data-yr');
            POST_changes.dates.end.qtr = last.getAttribute('data-qtr');
        }
    } else {
        /* If container has courses within it, we keep the container
           and remove all courses/put them back in unscheduled lists. */
        const req_container = document.getElementById('req-container');
        const elec_container = document.getElementById('elec-container');

        // Iterate over all courses in container
        while (course_container.children.length > 0) {
            let crs = course_container.children[0];
            // move to required/elective container as appropriate
            if (crs.getAttribute('data-req') === 'true'){
                req_container.insertBefore(crs, req_container.children[0]);
            } else {
                elec_container.insertBefore(crs, elec_container.children[0]);
            }
            // update save state object, index for dragging validation
            let crs_id = crs.getAttribute('data-id');
            POST_changes.courses[crs_id] = {year: null, qtr: null};
            crs_idx[crs_id] = -1;
        }
        // Add placeholder element
        let placeholder = new_placeholder();
        course_container.append(placeholder);
        // Unless qtr is first/last of sched, hide the [x] (can't delete inner quarters)
        if (!(course_container.parentNode === qtr_nodes[1]) && 
            !(course_container.parentNode === qtr_nodes[qtr_nodes.length - 2])){
                event.target.hidden = true;
            }
    }
}

// Factory for placeholder objects
function new_placeholder() {
    let placeholder = document.createElement('div');
    placeholder.setAttribute('class', 'course-item placeholder');
    let empty_title = document.createElement('span');
    empty_title.setAttribute('class', 'empty-title course-title');
    empty_title.innerHTML = '(empty term)';
    placeholder.appendChild(empty_title);

    return placeholder
}

/* Set initial indices of crs_idx on page load (for drag validation logic) */
const starting_nodes = Array.from(qtr_nodes);
for (var i = 1; i < starting_nodes.length - 1; ++i) {
    let nodes = starting_nodes[i].children[1].children;
    for (var node of nodes) {
        if (node.classList.contains('course')) {
            crs_idx[node.getAttribute('data-id')] = i;
        }
    }
}

/* CSRF token for fetch authentication */
const csrftoken = Cookies.get('csrftoken');