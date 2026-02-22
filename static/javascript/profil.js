// changer la photo de profil

document.addEventListener("DOMContentLoaded", function () {
    const input = document.querySelector('#profil-picture-input');
    const form = document.querySelector("#profil-picture-form");

    if (input && form) {
        input.addEventListener('change', function () {
            form.submit();
        });
    }
});

// message d'erreur au changement de donnée + bouton pour decendre automatiquement

document.addEventListener('DOMContentLoaded', () => {

    const passwordInput = document.querySelector('#new_password');
    const strengthBar = document.querySelector('#strength-bar');
    const requirementsList = document.querySelector('.password-requirements');

    if (passwordInput && strengthBar) {
        const requirements = {
            length: document.querySelector('#length'),
            uppercase: document.querySelector('#uppercase'),
            lowercase: document.querySelector('#lowercase'),
            number: document.querySelector('#number'),
            special: document.querySelector('#special')
        };

        document.addEventListener('click', (e) => {
            if (!passwordInput.contains(e.target) && !requirementsList.contains(e.target)) {
                if (requirementsList.classList.contains(('active'))) {
                    requirementsList.classList.remove('active');
                }
            }
        })

        passwordInput.addEventListener('input', () => {
            requirementsList.classList.add('active');
            const val = passwordInput.value;
            let score = 0;

            const criteria = {
                length: val.length >= 8,
                uppercase: /[A-Z]/.test(val),
                lowercase: /[a-z]/.test(val),
                number: /[0-9]/.test(val),
                special: /[!@#$%^&*(),.?":{}|<>]/.test(val)
            };

            for (const key in criteria) {
                const element = requirements[key];
                if (element) {
                    if (criteria[key]) {
                        element.classList.replace('invalid', 'valid');
                        score++;
                    } else {
                        element.classList.replace('valid', 'invalid');
                    }
                }
            }

            strengthBar.className = "strength-bar";
            if (val.length === 0) {
                strengthBar.style.width = "0%";
            } else if (score <= 2) {
                strengthBar.classList.add('weak');
                strengthBar.style.width = "33%";
            } else if (score <= 4) {
                strengthBar.classList.add('medium');
                strengthBar.style.width = "66%";
            } else {
                strengthBar.classList.add('strong');
                strengthBar.style.width = "100%";
            }
        });
    }

    const errorMessages = document.querySelectorAll(".error, .no-error");

    if (errorMessages) {
        if (errorMessages.length > 0) {
            document.addEventListener('click', () => {
                errorMessages.forEach(msg => msg.remove());
            });

            const targetProfil = document.querySelector('.section-profil')
            if (targetProfil) {
                targetProfil.scrollIntoView({
                    behavior: 'smooth',
                });
            }
        }
    }
});

// bouton pour afficher le bouton pour supprimer le compte 

const btnDelete = document.querySelector('.btn-delete')
const globalDelete = document.querySelector('.global-delete')
if (btnDelete) {
    btnDelete.addEventListener('click', () => {
        globalDelete.classList.toggle('active')
        btnDelete.classList.toggle('active')
    })
}

// bouton pour afficher le bouton pour se deconnecter du compte

const btnLogout = document.querySelector('.btn-logout')
const globalogout = document.querySelector('.global-logout')
if (btnLogout) {
    btnLogout.addEventListener('click', () => {
        globalogout.classList.toggle('active')
        btnLogout.classList.toggle('active')
    })
}

