// quiz

document.querySelectorAll('.btn-case').forEach(button => {
    button.addEventListener('click', (event) => {
        event.stopPropagation()

        const id = button.dataset.id
        const description = document.querySelector('.description[data-id="' + id + '"]')

        if (!description) return

        const isActive = description.classList.contains('active')

        document.querySelectorAll('.description').forEach(desc => {
            desc.classList.remove('active')
        })

        if (!isActive) {
            description.classList.add('active')
        }

        const backBtn = description.querySelector('.back-btn-3')
        if (backBtn) {
            backBtn.addEventListener('click', (e) => {
                e.stopPropagation()
                description.classList.remove('active')
            })
        }
    })
})

document.addEventListener('click', (e) => {
    document.querySelectorAll('.description.active').forEach(desc => {
        if (!desc.contains(e.target)) {
            desc.classList.remove('active')
        }
    })
})

// minuteur 

let timeLeft = 20;
let timerSpan = document.querySelector('#time');
let form = document.querySelector('form');

if (timerSpan) {
    let countdown = setInterval(() => {
        timeLeft--;
        timerSpan.textContent = timeLeft;

        if (timeLeft <= 0) {
            clearInterval(countdown);
            form.submit();
        }
    }, 1000);
}

// album 

document.querySelectorAll('.favorite-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const heart = btn.querySelector('.heart-icon');
        const carteId = btn.dataset.id;

        const isAlreadyFav = heart.classList.contains('ri-heart-fill');
        const newState = !isAlreadyFav; 

        fetch("/set_carte_favorite", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                carte: carteId,
                favorite: newState
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "ok") {

                    document.querySelectorAll('.heart-icon').forEach(h => {
                        h.classList.remove('ri-heart-fill');
                        h.classList.add('ri-heart-line');
                    });

                    if (newState) {
                        heart.classList.remove('ri-heart-line');
                        heart.classList.add('ri-heart-fill');
                    }
                }
            });
    });
});