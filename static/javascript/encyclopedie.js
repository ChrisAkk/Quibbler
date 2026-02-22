// ===========================
// Fonction principale Encyclopédie
// ===========================

let btnTitreActif = null;
let btnSousTitreActif = null;
let btnNomActif = null;

function getEncyclopediaParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        theme: params.get("theme"),
        chapitre: params.get("chapitre"),
        nom: params.get("nom")
    };
}

// Initialisation de l'encyclopédie

function initEncyclopedie() {
    const col1 = document.querySelector(".col-1");
    const col2 = document.querySelector(".col-2");
    const col3 = document.querySelector(".col-3");
    const col4 = document.querySelector(".col-4");

    const globalcol1 = document.querySelector("#global-col-1");
    const globalcol2 = document.querySelector("#global-col-2");
    const globalcol3 = document.querySelector("#global-col-3");
    const globalcol4 = document.querySelector("#global-col-4");

    if (!col1 || !col2 || !col3 || !col4) return console.error("Colonnes manquantes");

    globalcol1.classList.add("visible2");
    globalcol2.classList.remove("visible2");
    globalcol3.classList.remove("visible2");
    globalcol4.classList.remove("visible2");

    fetch("/static/json/encyclopedia.json")
        .then(res => res.ok ? res.json() : Promise.reject("Erreur HTTP " + res.status))
        .then(data => {
            for (let titre in data.encyclopedia) {
                const btn = document.createElement("button");
                btn.textContent = titre;

                btn.addEventListener("click", () => {
                    if (btnTitreActif === btn) {
                        btn.classList.remove("active");
                        col2.innerHTML = "";
                        col3.innerHTML = "";
                        col4.innerHTML = "";
                        globalcol2.classList.remove("visible2");
                        globalcol3.classList.remove("visible2");
                        globalcol4.classList.remove("visible2");
                        btnTitreActif = btnSousTitreActif = btnNomActif = null;
                        return;
                    }

                    if (btnTitreActif) btnTitreActif.classList.remove("active");
                    btn.classList.add("active");
                    btnTitreActif = btn;

                    col2.innerHTML = "";
                    col3.innerHTML = "";
                    col4.innerHTML = "";
                    btnSousTitreActif = btnNomActif = null;

                    globalcol2.classList.add("visible2");
                    globalcol3.classList.remove("visible2");
                    globalcol4.classList.remove("visible2");

                    const sousTitres = data.encyclopedia[titre];
                    for (let sous in sousTitres) {
                        const btnSous = document.createElement("button");
                        btnSous.textContent = sous;

                        btnSous.addEventListener("click", () => {
                            if (btnSousTitreActif === btnSous) {
                                btnSous.classList.remove("active");
                                col3.innerHTML = "";
                                col4.innerHTML = "";
                                globalcol3.classList.remove("visible2");
                                globalcol4.classList.remove("visible2");
                                btnSousTitreActif = btnNomActif = null;
                                return;
                            }

                            if (btnSousTitreActif) btnSousTitreActif.classList.remove("active");
                            btnSous.classList.add("active");
                            btnSousTitreActif = btnSous;

                            col3.innerHTML = "";
                            col4.innerHTML = "";
                            btnNomActif = null;

                            globalcol3.classList.add("visible2");
                            globalcol4.classList.remove("visible2");

                            const items = data.encyclopedia[titre][sous];
                            items.forEach(item => {
                                if (item.nom) {
                                    const btnNom = document.createElement("button");
                                    btnNom.textContent = item.nom;

                                    btnNom.addEventListener("click", () => {
                                        if (btnNomActif === btnNom) {
                                            btnNom.classList.remove("active");
                                            col4.innerHTML = "";
                                            globalcol4.classList.remove("visible2");
                                            btnNomActif = null;
                                            return;
                                        }
                                        if (btnNomActif) btnNomActif.classList.remove("active");
                                        btnNom.classList.add("active");
                                        btnNomActif = btnNom;

                                        col4.innerHTML = item.description || "";
                                        globalcol4.classList.add("visible2");
                                    });

                                    col3.appendChild(btnNom);
                                }
                            });
                        });

                        col2.appendChild(btnSous);
                    }
                });

                col1.appendChild(btn);
            }

            const { theme, chapitre, nom } = getEncyclopediaParams();

            if (theme) {
                const themeBtn = [...col1.children]
                    .find(b => b.textContent === theme);
                if (themeBtn) themeBtn.click();
            }

            setTimeout(() => {
                if (chapitre) {
                    const chapitreBtn = [...col2.children]
                        .find(b => b.textContent === chapitre);
                    if (chapitreBtn) chapitreBtn.click();
                }
            }, 50);

            setTimeout(() => {
                if (nom) {
                    const nomBtn = [...col3.children]
                        .find(b => b.textContent === nom);
                    if (nomBtn) nomBtn.click();
                }
            }, 100);

        })
        .catch(err => console.error("Erreur fetch ou JSON :", err));
}

// Barre de recherche + Bouton retour

function initSearchAndBackButton() {
    const searchBar = document.querySelector(".global-search-bar input");
    const backButton = document.querySelector(".global-search-bar button");
    const cols = [
        document.querySelector("#global-col-1"),
        document.querySelector("#global-col-2"),
        document.querySelector("#global-col-3"),
        document.querySelector("#global-col-4")
    ];
    let currentStep = 0;
    let historySteps = [];

    function showColumn(index) {
        cols.forEach((col, i) => {
            if (i === index) {
                col.classList.add("visible2");
                col.style.display = "flex";
            } else {
                col.classList.remove("visible2");
                col.style.display = "none";
            }
        });
        backButton.style.display = historySteps.length > 0 ? "inline-flex" : "none";
        currentStep = index;
    }
    function resetActiveButtonsFromStep(step) {
        if (step <= 1 && btnTitreActif) { btnTitreActif.classList.remove("active"); btnTitreActif = null; }
        if (step <= 2 && btnSousTitreActif) { btnSousTitreActif.classList.remove("active"); btnSousTitreActif = null; }
        if (step <= 3 && btnNomActif) { btnNomActif.classList.remove("active"); btnNomActif = null; }
    }

    if (searchBar) {
        searchBar.addEventListener("input", () => {
            const query = searchBar.value.toLowerCase();
            const allButtons = document.querySelectorAll(".col-1 button, .col-2 button, .col-3 button");
            allButtons.forEach(btn => {
                const text = btn.textContent.toLowerCase();
                btn.style.display = text.includes(query) ? "block" : "none";
            });
        });
    }



    function handleMobileView() {
        if (window.innerWidth <= 1024) {
            showColumn(0);

            backButton.onclick = () => {
                if (historySteps.length > 0) {
                    const prevStep = historySteps.pop();
                    showColumn(prevStep);
                }
            };

            document.body.onclick = e => {
                const btn = e.target.closest("button");
                if (!btn) return;

                let nextStep = null;
                if (btn.closest(".col-1")) nextStep = 1;
                else if (btn.closest(".col-2")) nextStep = 2;
                else if (btn.closest(".col-3")) nextStep = 3;

                if (nextStep !== null && nextStep !== currentStep) {
                    console.log("Étape ajoutée à l'historique :", currentStep); 
                    resetActiveButtonsFromStep(nextStep);
                    historySteps.push(currentStep);
                    showColumn(nextStep);
                }
            };
        }
    }

    window.addEventListener("resize", handleMobileView);
    handleMobileView();
}

document.addEventListener("DOMContentLoaded", () => {
    initEncyclopedie();
    initSearchAndBackButton();
});

// animal favori 

const btns = document.querySelectorAll('.btn-choix');

btns.forEach(btn => {
    btn.addEventListener('click', () => {
        const animal = btn.dataset.animal;
        const isActive = btn.classList.contains('active')

        if (isActive) {
            btn.classList.remove('active');

            fetch("/set_animal_favorite", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ animal: "" })
            });
        }

        else {
            btns.forEach(b => b.classList.remove('active'));

            btn.classList.add('active');

            fetch("/set_animal_favorite", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ animal: animal })
            });
        }
    });
});

fetch("/get_animal_favorite")
    .then(r => r.json())
    .then(data => {
        if (data.animal) {
            const selected = document.querySelector(`.btn-choix[data-animal="${data.animal}"]`);
            if (selected) selected.classList.add('active');
        }
    });