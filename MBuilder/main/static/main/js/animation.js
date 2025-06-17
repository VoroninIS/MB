const qsa = (s, o = document) => o.querySelectorAll(s);
const qs = (s, o = document) => o.querySelector(s);


// Кнопка генерации
qsa('.round-button').forEach(el => el.addEventListener('mousemove', function(e) {
    const pos = this.getBoundingClientRect();
    const mx = e.clientX - pos.left - pos.width/2; 
    const my = e.clientY - pos.top - pos.height/2;
    
    this.style.transition = 'transform .1s linear, background-color 0.2s ease-in';
    this.children[0].style.transition = 'transform .1s linear';
    this.style.transform = 'translate('+ mx * 0.8 +'px, '+ my * 0.8 +'px)';
    this.style.transform += 'rotate3d('+ mx * -1 +', '+ my * -0.5 +', 0, 12deg)';
    this.children[0].style.transform = 'translate('+ mx * 0.2 +'px, '+ my * 0.2 +'px)';
}));

qsa('.round-button').forEach(el => el.addEventListener('mouseleave', function() {
    this.style.transform = 'translate3d(0px, 0px, 0px)';
    this.style.transform += 'rotate3d(0, 0, 0, 0deg)';
    this.style.transition = 'transform 0.5s ease-in-out, background-color 0.5s ease-in';
    this.children[0].style.transition = 'transform 0.5s ease-in-out';
    setTimeout("document.querySelector('.generate-icon').style.transition = 'transform .1s ease-in-out';", 500)
    setTimeout("document.querySelector('.generate-icon').style.transition = 'transform .1s ease-in-out';", 500)
    this.children[0].style.transform = 'translate3d(0px, 0px, 0px)';
}));


// Курсор
var cursor = document.querySelector('.cursor');
var cursorinner = document.querySelector('.cursor2');
var interactive = document.querySelectorAll('a, input, button, label');

function handleFirstMove() {
    cursor.style.display = 'block';
    cursorinner.style.display = 'block';

    document.removeEventListener('mousemove', handleFirstMove);
}
document.addEventListener('mousemove', handleFirstMove);

document.addEventListener('mousemove', function(e){
    var x = e.clientX;
    var y = e.clientY;
    cursor.style.transform = `translate3d(calc(${e.clientX}px - 50%), calc(${e.clientY}px - 50%), 0)`
});

document.addEventListener('mousemove', function(e){
    var x = e.clientX;
    var y = e.clientY;
    cursorinner.style.left = x + 'px';
    cursorinner.style.top = y + 'px';
});

document.addEventListener('mousedown', function(){
    cursor.classList.add('click');
    cursorinner.classList.add('cursorinnerhover')
});

document.addEventListener('mouseup', function(){
    cursor.classList.remove('click')
    cursorinner.classList.remove('cursorinnerhover')
});

interactive.forEach(item => {
    item.addEventListener('mouseover', () => {
        cursor.classList.add('hover');
    });
    item.addEventListener('mouseleave', () => {
        cursor.classList.remove('hover');
    });
})
