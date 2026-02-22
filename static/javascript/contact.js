document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#contact-form');
    const cooldownMsg = document.querySelector('#cooldown-message');
    const cooldownDuration = 60 * 60 * 1000; // 1h
    const userId = document.body.dataset.userId;
    const storageKey = `lastSent_${userId}`;

    function startCooldown() {
        const endTime = Date.now() + cooldownDuration;
        localStorage.setItem(storageKey, endTime);
        updateCooldown();
    }

    function updateCooldown() {
        const endTime = localStorage.getItem(storageKey);
        if (!endTime) return;

        const timeLeft = endTime - Date.now();

        if (timeLeft > 0) {
            form.classList.add('active');
            cooldownMsg.style.display = 'block';
            const minutes = Math.floor(timeLeft / 60000);
            const secondes = Math.floor((timeLeft % 60000) / 1000);
            const secondesFormatted = String(secondes).padStart(2, '0'); 
            cooldownMsg.innerHTML = `
                    <div style="text-align:center;">
                        <i class="ri-checkbox-circle-line cooldown-icon"></i>
                        <p id="cooldown-timer">${minutes}:${secondesFormatted}</p>
                    </div>
                `;

            setTimeout(updateCooldown, 1000);
        }
        else {
            form.classList.remove('active');
            cooldownMsg.style.display = 'none';
            localStorage.removeItem(storageKey);
        }
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            startCooldown();
            form.submit();
        });
    }

    updateCooldown();
});
