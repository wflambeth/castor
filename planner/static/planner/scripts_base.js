"use strict";

var drake = dragula({
  isContainer: function (el) {
    return el.classList.contains('course-container');
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
  }
}