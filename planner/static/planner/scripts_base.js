"use strict";

const COURSE_COLOR_DRAG = '#05ff77';
const COURSE_COLOR_NORM = 'beige';
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
        target.previousElementSibling.children[0].hidden = false;
      }
    }
    // add placeholder to newly-empty container
    if (source.getElementsByClassName('course-item').length === 0) {
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

if (Object.keys(prereqs).length > 0) { // to avoid issues with logged-out demo page; soon to be fixed
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
          terms[i].firstElementChild.style.background = TERM_COLOR_DRAG; // 
        }
      }
    }
  }

  // ends highlights on all terms/courses upon drag end
  function endHighlights(el) {
    let courses = document.getElementsByClassName('course');
    for (var course of courses) {
      course.style.background = COURSE_COLOR_NORM;
    }
    let terms = Array.from(qtr_nodes);
    for (var i = 1; i < terms.length - 1; ++i){
      terms[i].firstElementChild.style.background = TERM_COLOR_NORM;
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