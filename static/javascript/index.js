
// password requierment

document.addEventListener('DOMContentLoaded', () => {

    const passwordInput = document.querySelector('#new-password');
    const strengthBar = document.querySelector('#strength-bar');
    const requirementsList = document.querySelector('.password-requirements')

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

    // etincelle

    const errorMessages = document.querySelectorAll(".error");
    if (errorMessages.length > 0) {
        const removeErrors = () => {
            errorMessages.forEach(msg => msg.remove());
            document.removeEventListener('click', removeErrors);
        };
        document.addEventListener('click', removeErrors);
    }
});

// etincelle
document.addEventListener('mousemove', (e) => {
    const spark = document.createElement('div');
    spark.classList.add('spark');
    spark.style.left = e.pageX + 'px';
    spark.style.top = e.pageY + 'px';
    document.body.appendChild(spark);
    setTimeout(() => spark.remove(), 600);
});