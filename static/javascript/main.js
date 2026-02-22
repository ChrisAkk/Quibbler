
// image d'apparition

cloud = document.querySelector(".cloud")

if (cloud) {
    window.addEventListener('load', () => {
        cloud.classList.add("loaded");
    })
}

// bouton de scroll

const scrollBtn = document.querySelector("#scroll-btn")
if (scrollBtn) {
    scrollBtn.addEventListener('click', Scroll)
    function Scroll() {
        const target = document.querySelector('.section-2')
        target.scrollIntoView({
            behavior: 'smooth',
        });
    }
}

// bouton retour

const backBtn = document.querySelector('#back-btn')
if (backBtn) {
    backBtn.addEventListener('click', Back)

    function Back() {
        window.history.back();
    }
}

const backBtn2 = document.querySelector('#back-btn-2')
if (backBtn2) {
    backBtn2.addEventListener('click', Back)

    function Back() {
        window.history.back();
    }
}

// etincelle 

let sparkEnabled = true;

fetch('/get_spark')
    .then(r => r.json())
    .then(data => {
        sparkEnabled = data.enabled;

        const btnSpark = document.querySelector('.btn-spark');
        if (btnSpark) {
            btnSpark.classList.toggle('active', sparkEnabled);

            btnSpark.addEventListener('click', () => {
                sparkEnabled = !sparkEnabled;

                btnSpark.classList.toggle('active', sparkEnabled);

                fetch('/toggle_spark', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: sparkEnabled })
                });
            });
        }
    });

document.addEventListener('mousemove', (e) => {
    if (!sparkEnabled) return;

    const spark = document.createElement('div');
    spark.classList.add('spark');
    spark.style.left = e.pageX + 'px';
    spark.style.top = e.pageY + 'px';
    document.body.appendChild(spark);

    setTimeout(() => {
        spark.remove();
    }, 600);
});




// header

const header = document.querySelector("header")
const main = document.querySelector('main')

if (header && main) {
    let position = 0;
    const hideHeader = 200;

    window.addEventListener("scroll", () => {
        const scrollTop = window.scrollY;

        if (scrollTop > hideHeader) {
            if (scrollTop > position) {
                header.classList.add("header-hidden");
            }
            else {
                header.classList.remove("header-hidden");
            }
        }
        else {
            header.classList.remove("header-hidden");
        }

        if (scrollTop > 100) {
            header.classList.add("scrolled");
        }
        else {
            header.classList.remove("scrolled");
        }

        if (scrollTop <= 0) {
            position = 0;
        }
        else {
            position = scrollTop;
        }

    })

    main.style.paddingTop = header.offsetHeight + 'px';
}

const menuHeader = document.querySelector('.profil-menu')
const menuBtn = document.querySelector('.menu-btn')

if (menuHeader && menuBtn) {
    menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menuHeader.classList.toggle('active');
        menuBtn.classList.toggle('active');

        if (header) {
            header.classList.toggle('active');
        }
    })

    document.addEventListener('click', (e) => {
        if (!menuHeader.contains(e.target) && menuHeader.classList.contains('active')) {
            menuHeader.classList.remove('active');
            menuBtn.classList.remove('active');
            if (header) {
                header.classList.remove('active');
            }
        }
    })

    window.addEventListener('scroll', () => {
        if (menuHeader.classList.contains('active')) {
            menuHeader.classList.remove('active');
            menuBtn.classList.remove('active');
            if (header) {
                header.classList.remove('active');
            }
        }
    })

}

const menuHeaderPhone = document.querySelector('.phone-menu')
const menuBtnPhone = document.querySelector('.menu-btn-phone')

if (menuHeaderPhone && menuBtnPhone) {
    menuBtnPhone.addEventListener('click', (e) => {
        e.stopPropagation();
        menuHeaderPhone.classList.toggle('active');
        menuBtnPhone.classList.toggle('active');

        if (header) {
            header.classList.toggle('active');
        }
    })

    document.addEventListener('click', (e) => {
        if (!menuHeaderPhone.contains(e.target) && menuHeaderPhone.classList.contains('active')) {
            menuHeaderPhone.classList.remove('active');
            menuBtnPhone.classList.remove('active');
            if (header) {
                header.classList.remove('active');
            }
        }
    })

    window.addEventListener('scroll', () => {
        if (menuHeaderPhone.classList.contains('active')) {
            menuHeaderPhone.classList.remove('active');
            menuBtnPhone.classList.remove('active');
            if (header) {
                header.classList.remove('active');
            }
        }
    })

}