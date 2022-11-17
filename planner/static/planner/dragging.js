var drake = dragula({
    isContainer: function (el) {
      return el.classList.contains('course-container');
    }
  });