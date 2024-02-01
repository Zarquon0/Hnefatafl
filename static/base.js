const popup = (msg) => {
    if (document.getElementById('popup_bgrnd')) {
        closePopup();
    }
    let popupBgrnd = document.createElement('div');
    popupBgrnd.id = 'popup_bgrnd';
    popupBgrnd.innerHTML = `<div><p>${msg}</p></div>`;
    let close = document.createElement('img');
    close.id = 'close';
    close.src = '/static/media/X_icon.png';
    close.addEventListener('click', closePopup);
    document.body.appendChild(popupBgrnd);
    popupBgrnd.children[0].appendChild(close);
}

const closePopup = () => {
    let popupEl = document.getElementById('popup_bgrnd');
    if (popupEl) {
        document.body.removeChild(popupEl);
    }
}

if (flashed_msgs.length > 0) {
    let flashes = flashed_msgs.join('\n');
    popup(flashes);
}

let checked = false;
const checkWidth = () => {
    if (window.innerWidth <= 1000 && !checked) {
        popup('A wider screen is suggested for viewing this webpage.')
        checked = true;
    } else if (window.innerWidth > 1000 && checked) {
        closePopup();
        checked = false;
    }
}

window.addEventListener('resize', checkWidth);
checkWidth();