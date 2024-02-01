//Handle password reenter field appearance/disappearance
const pword = document.querySelectorAll('input[type="password"]')[0];
const reenter = document.getElementsByClassName('ipt_cont')[2];
pword.addEventListener('input', () => {
    if (pword.value) {
        reenter.style.display = 'block';
    } else {
        reenter.style.display = 'none';
    }
});

//Validate entered passwords are the same
const form = document.getElementsByTagName('form')[0];
form.addEventListener('submit', (e) => {
    let pwords = document.querySelectorAll('input[type="password"]');
    if (pwords[0].value != pwords[1].value){
        e.preventDefault();
        pwords[1].value = '';
        pwords[1].placeholder = 'Passwords must match';
    }
})

