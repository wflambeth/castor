"use strict";

const COURSE_COLOR_DRAG = '#7A3D00';
const COURSE_COLOR_NORM = '#FFFAF3';
const TERM_COLOR_DRAG = 'lightgreen';
const TERM_COLOR_NORM = '';

var drake = dragula({
  isContainer: function (el) {
    return el.classList.contains('course-container');
  },
  moves: function (el) {
    return (!el.classList.contains('placeholder'));
  },
  accepts: function (el, target, source, sibling) {
    /* 
    Determines whether a course is eligible to be dropped in a given term. 
    This is true if the course is offered that quarter, and if all prereqs have been 
    scheduled previously. 
    */
    if (POST_changes['s'] !== 'NULL') { // TODO: Hack to avoid issues with logged-out demo page; remove
      // course containers always accept their children back to them
      let target_id = target.getAttribute('id');
      let required = el.getAttribute('data-req') === 'true' ? true : false;
      if (target_id === "req-container") {
        return required;
      }
      else if (target_id === "elec-container") {
        return (!required);
      }
      // check that item can be dropped in this quarter - return false if it cannot
      let item_id = +el.getAttribute('data-id');
      let target_qtr = +target.parentNode.getAttribute('data-qtr');
      if (quarters[item_id].indexOf(target_qtr) === -1) {
        return false;
      }
      // find index of target qtr, pull course prereqs
      let target_index = Array.from(qtr_nodes).indexOf(target.parentNode);
      for (var prq of prereqs[item_id]) {
        // if any prereqs are unplaced or placed equal to/after target, return false
        if (crs_idx[prq] === -1 || crs_idx[prq] >= target_index) {
          return false;
        }
      }
    }
    // otherwise, all looks good! 
    return true;
  },
});

drake.on('drop', dropLogger);

function dropLogger(el, target, source, sibling) {
  /* 
  Handles any drop events when an item is being dragged. 
  Updates changes to send to DB, adds/removes placeholders for empty qtrs, 
    and tracks index of each course within the schedule.
  */
  if (target !== source) {
    // Update changes to be saved
    let id = el.getAttribute('data-id');
    let year = target.getAttribute('data-yr');
    let qtr = target.getAttribute('data-qtr');
    POST_changes.courses[id] = { year, qtr };

    // Remove placeholder from newly-nonempty container
    let placeholder = target.getElementsByClassName('placeholder')[0];
    if (placeholder != undefined) {
      placeholder.remove();
      // check for existence of qtr-delete node, and enable if exists
      if (target.previousElementSibling.children.length > 0) {
        target.previousElementSibling.children[1].hidden = false;
      }
    }
    // add placeholder to newly-empty container
    if (source.getElementsByClassName('course-item').length === 0
        && source.getAttribute('id') !== 'req-container'
        && source.getAttribute('id') !== 'elec-container') {
      // check if a spare placeholder is handy, make one if not
      if (placeholder === undefined) {
        placeholder = new_placeholder();
      }
      source.appendChild(placeholder);
    }
    // Update index of courses for validating drops
    let curr_nodes = Array.from(qtr_nodes);
    let this_index = curr_nodes.indexOf(target.parentNode);
    crs_idx[id] = this_index;
  }
}

drake.on('drag', dragHighlighter);
drake.on('dragend', endHighlights);

// Highlights prereqs and valid drop terms, when a course is dragged
function dragHighlighter(el, source) {
  let course_id = el.getAttribute('data-id');
  
  // highlight prereqs
  let course_prqs = prereqs[course_id];
  let prq_elements = []
  for (var prq_id of course_prqs) { // find prereq elements
    prq_elements.push(document.querySelector('[data-id="' + prq_id + '"]'));
  } 
  for (var elem of prq_elements) { // set a background color on them
    elem.style.background = COURSE_COLOR_DRAG;
    elem.style.color = 'white';
  }

  // highlight terms
  let terms = Array.from(qtr_nodes);
  // returns index of latest-placed prereq, or -1 (if prqs still unplaced) or 0 (if no prqs)
  let final_prq_idx = getFinalPrqIdx(prereqs[course_id], crs_idx);
  if (final_prq_idx > -1) { 
  let course_qtrs = quarters[course_id];
    for (var i = final_prq_idx + 1; i < terms.length - 1; ++i){ // iterator avoids first/last items in the array, which are add-term buttons
      let this_qtr = terms[i].getAttribute('data-qtr');
      if (course_qtrs.includes(+this_qtr)) {
        terms[i].children[1].style.outline = "4px groove " + TERM_COLOR_DRAG; // 
      }
    }
  }
}

// ends highlights on all terms/courses upon drag end
function endHighlights(el) {
  let courses = document.getElementsByClassName('course');
  for (var course of courses) {
    course.style.background = COURSE_COLOR_NORM;
    course.style.color = 'black';
  }
  let terms = Array.from(qtr_nodes);
  for (var i = 1; i < terms.length - 1; ++i){
    terms[i].children[1].style.outline = "";
  }
}

// returns -1 to signal prereq not placed
// returns 0 if course has no prereqs
// otherwise, returns index of final prereq placed in schedule
function getFinalPrqIdx(crs_prq, crs_idx){
  if (crs_prq.length == 0){
    return 0;
  }
  let index = -1;
  for (var prereq of crs_prq){
    let prq_idx = crs_idx[prereq];
    if (prq_idx == -1){
      return -1;
    }
    else if (prq_idx > index){
      index = prq_idx;
    }
  }
  return index;
}

/* Note to self: scripts previously hosted in scripts_auth.js live past this point */
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
  let title_span = document.createElement('span');
  title_span.setAttribute('class', 'term-title-span');
  title_span.innerHTML = qtr_map[qtr] + ' ' + yr + ' ';
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
  
  title.appendChild(title_span);
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
  schedule_wrapper.insertBefore(newtop, topnode);
  
  // Ensure [x]es are revealed/hidden appropriately on former edge
  // (Hidden if node is not on end, and is empty)
  if (qtr_nodes.length > 4 && (topnode.children[1].children[0].classList.contains('placeholder'))) {
      topnode.children[0].children[1].hidden = true;
  } else if (qtr_nodes.length === 4) { // allow deletion of bottom node if top node has been added
      qtr_nodes[2].children[0].children[1].hidden = false;
  }

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
  schedule_wrapper.insertBefore(newbottom, bottomnode.nextSibling);

  // Ensure [x]es are revealed/hidden appropriately on former edge
  // (Hidden if node is not on end, and is empty)
  if (qtr_nodes.length > 4 && (bottomnode.children[1].children[0].classList.contains('placeholder'))) {
      bottomnode.children[0].children[1].hidden = true;
  } else if (qtr_nodes.length === 4) { // allow deletion of top node if bottom node has been added
      qtr_nodes[1].children[0].children[1].hidden = false;
  }
  

  // Update schedule bounds to be saved to DB
  POST_changes.dates.end.year = yr;
  POST_changes.dates.end.qtr = qtr;
  console.log(POST_changes);
});

// hide delete buttons for non-empty and non-edge terms 
// TODO: why am I using window.onload here, better way to structure this? 
window.onload = (event) => {    
  // add event listeners 
  for (var i = 1; i < qtr_nodes.length - 1; ++i) {
      qtr_nodes[i].children[0].children[1].addEventListener('click', update_qtrs);
  }
  // ensure first & last qtrs are deleteable, as long as there is > 1 qtr
  if (qtr_nodes.length > 3) {
      qtr_nodes[1].children[0].children[1].hidden = false;
      qtr_nodes[qtr_nodes.length - 2].children[0].children[1].hidden = false;
  }
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
          first.children[0].children[1].hidden = false;

          // update save state with new bounds
          POST_changes.dates.start.year = first.getAttribute('data-yr');
          POST_changes.dates.start.qtr = first.getAttribute('data-qtr');

          // Decrement course indices
          for (const [key, value] of Object.entries(crs_idx)){
              if (value !== -1) {
                  crs_idx[key] -= 1;
              }
          }
      } else if (qtr_nodes[qtr_nodes.length - 2].children[1] === course_container) {
          // still kick things off by nuking said element
          event.target.parentNode.parentNode.remove();

          // get new last from qtr_nodes, set [x] visible
          let last = qtr_nodes[qtr_nodes.length - 2];
          last.children[0].children[1].hidden = false;

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
  // Attempt to handle edge cases around creating/destroying qtrs when
  // there are 2 or fewer in schedule
  if (qtr_nodes.length === 3) {
      qtr_nodes[1].children[0].children[1].hidden = true;
  } else if (qtr_nodes.length === 4) {
      qtr_nodes[1].children[0].children[1].hidden = false;
      qtr_nodes[2].children[0].children[1].hidden = false;
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