var drake = dragula();

ctnrs = document.querySelectorAll('.course-container');

for (i = 0; i < ctnrs.length; ++i){
    drake.containers.push(ctnrs[i]);
}