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
    let id = el.getAttribute('data-id');
    let year = target.getAttribute('data-yr');
    let qtr = target.getAttribute('data-qtr');
    console.log(id, year, qtr);
    POST_changes.courses[id] = { year, qtr };

    let placeholder = target.getElementsByClassName('empty-item')[0];
    if (placeholder != undefined) {
      placeholder.remove();
      // check for existence of qtr-delete node (if user is logged in)
      if (target.previousElementSibling.children.length > 0) {
        // enable the delete button to clear that qtr
        target.previousElementSibling.children[0].hidden = false;
      }
    }

    if (source.getElementsByClassName('course-item').length === 0){
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
  }
}