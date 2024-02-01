//Adjust header spacer
const rootUrl = 'http://127.0.0.1'

//Music stuff
const sound = document.getElementsByTagName('audio')[0];
const sound_button = document.getElementById('sound');

const add_sound = () => {
    sound.play();
    sound_button.innerHTML = 'Mute';
    sound_button.removeEventListener('click', add_sound);
    sound_button.addEventListener('click', pause_sound);
}
const pause_sound = () => {
    sound.pause();
    sound_button.innerHTML = 'Unmute';
    sound_button.removeEventListener('click', pause_sound);
    sound_button.addEventListener('click', add_sound);
}

sound_button.addEventListener('click', add_sound);

//Challenge Buttons
/*
const challenge = (user_id) => {
    fetch(rootUrl + '/new_game',
    method = 'POST',
    headers = {'Content-type' : 'application/json'},
    body = JSON.stringify({
        uid : user_id
    })).then()
}
*/