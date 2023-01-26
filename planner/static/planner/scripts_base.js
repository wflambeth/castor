"use strict";

var drake = dragula({
  isContainer: function (el) {
    return el.classList.contains('course-container');
  },
  moves: function (el) {
    return (!el.classList.contains('empty-item'));
  }
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
    let placeholder = target.getElementsByClassName('empty-item')[0];
    if (placeholder != undefined) {
      placeholder.remove();
      // check for existence of qtr-delete node, and enable if exists
      if (target.previousElementSibling.children.length > 0) {
        target.previousElementSibling.children[0].hidden = false;
      }
    }

    // add placeholder to newly-empty container
    // TODO: replace with function defined in scripts_auth.js
    if (source.getElementsByClassName('course-item').length === 0){
      // check if a spare placeholder is handy, use it if so
      if (placeholder === undefined){
        placeholder = document.createElement('div');
        placeholder.setAttribute('class', 'course-item empty-item placeholder');
        let empty_title = document.createElement('span');
        empty_title.setAttribute('class', 'empty-title course-title');
        empty_title.innerHTML = 'placeholder: empty term';
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