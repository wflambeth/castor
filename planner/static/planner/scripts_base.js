"use strict";

var drake = dragula({
  isContainer: function (el) {
    return el.classList.contains('course-container');
  },
  moves: function (el) {
    return (!el.classList.contains('placeholder'));
  },
  accepts: function (el, target, source, sibling) {
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
      // check that item can be dropped in a given quarter - return false if it cannot
      let item_id = +el.getAttribute('data-id');
      let target_qtr = +target.parentNode.getAttribute('data-qtr');
      if (quarters[item_id].indexOf(target_qtr) === -1) {
        return false;
      }
      // check that all prereqs are in place
      let target_index = Array.from(qtr_nodes).indexOf(target.parentNode);
      for (var prq of prereqs[item_id]) {
        console.log(crs_idx[prq]);
        // if any are unplaced or placed equal to/after target, return false
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
    // TODO: replace with function defined in scripts_auth.js
    if (source.getElementsByClassName('course-item').length === 0) {
      // check if a spare placeholder is handy, use it if so
      if (placeholder === undefined) {
        placeholder = document.createElement('div');
        placeholder.setAttribute('class', 'course-item placeholder');
        let empty_title = document.createElement('span');
        empty_title.setAttribute('class', 'empty-title course-title');
        empty_title.innerHTML = '(empty term)';
        placeholder.appendChild(empty_title);
      }
      source.appendChild(placeholder);
    }
    // Update index of courses for validation purposes
    let curr_nodes = Array.from(qtr_nodes);
    let this_index = curr_nodes.indexOf(target.parentNode);
    crs_idx[id] = this_index;
  }
}