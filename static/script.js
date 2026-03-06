// Ta configuration Firebase
const firebaseConfig = {
  apiKey: "AIzaSyC6DYgQtPsoiFZvZRricLxmxTbhaFPGd_E",
  authDomain: "polycode-pro-4f91f.firebaseapp.com",
  projectId: "polycode-pro-4f91f",
  storageBucket: "polycode-pro-4f91f.firebasestorage.app",
  messagingSenderId: "836709270922",
  appId: "1:836709270922:web:a0c3f75dc9d127eb95b473"
};

// Initialisation
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Dire à Firebase de rester connecté
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL)
  .then(() => {
    console.log("Mémoire active");
  })
  .catch((error) => console.error("Erreur memoire:", error));

auth.onAuthStateChanged((user) => {
    const ecranLogin = document.getElementById('auth-screen');
    const ecranApp = document.getElementById('terminal-screen'); // Vérifie bien cet ID !

    if (user) {
        // CONNECTÉ
        if(ecranLogin) ecranLogin.style.display = 'none';
        if(ecranApp) ecranApp.style.display = 'block';
        console.log("Utilisateur connecté :", user.displayName);
    } else {
        // DÉCONNECTÉ
        if(ecranLogin) ecranLogin.style.display = 'flex';
        if(ecranApp) ecranApp.style.display = 'none';
        console.log("Utilisateur déconnecté");
    }
});

// Fonction pour déclencher la connexion Google
function connexionGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider).catch((error) => {
        alert("Erreur : " + error.message);
    });
}

function deconnexion() {
    auth.signOut().then(() => {
        alert("Déconnexion réussie ! À bientôt.");
    }).catch((error) => {
        console.error("Erreur de déconnexion:", error);
    });
}

// --- ÉLÉMENTS DU DOM ---
const editor = document.getElementById('editor');
const highlightLayer = document.getElementById('highlight-layer');
const lineNumbers = document.getElementById('line-numbers');
const langSelect = document.getElementById('lang-select'); // Scilab/Python
const consoleOut = document.getElementById('console-bottom');
const body = document.body;

// --- 1. DICTIONNAIRE DE TRADUCTION ---
const translations = {
    fr: {
        run: "LANCER ▶",
        clear: "EFFACER",
        ai: "+ Aide IA",
        ready: "Console prête...",
        loading: "⚡ Exécution en cours...",
        ia_thinking: "🤖 IA en réflexion...",
        auth_btn: "Entrer dans le Terminal",
        placeholder: "Veuillez entrer votre nom...",
        flag: "🇫🇷"
    },
    en: {
        run: "RUN ▶",
        clear: "CLEAR",
        ai: "+ AI Help",
        ready: "Console ready...",
        loading: "⚡ Executing...",
        ia_thinking: "🤖 IA thinking...",
        auth_btn: "Enter Terminal",
        placeholder: "Please enter your name...",
        flag: "🇺🇸"
    }
};

// --- 2. GESTION DE L'ÉDITEUR & SAUVEGARDE ---
function updateEditor() {
    const code = editor.value; 
    const lang = langSelect.value;

    // SAUVEGARDE AUTOMATIQUE
    localStorage.setItem('polycode_saved_code', code);

    const lines = code.split('\n');
    lineNumbers.innerHTML = lines.map((_, i) => `<div style="height: 24px;">${i + 1}</div>`).join('');

    let safeCode = code
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    let prismLang = lang === 'scilab' ? 'matlab' : lang;
    highlightLayer.className = `language-${prismLang}`;
    highlightLayer.innerHTML = safeCode;
    
    if (window.Prism) {
        Prism.highlightElement(highlightLayer);
    }
    syncScroll();
}

// Charger les données au démarrage
window.addEventListener('load', () => {
    // Restaurer le code
    const savedCode = localStorage.getItem('polycode_saved_code');
    if (savedCode) {
        editor.value = savedCode;
    }
    
    // Restaurer le thème
    if (localStorage.getItem('polycode_theme') === 'light') {
        body.classList.add('light-mode');
    }

    // Restaurer la langue
    appliquerLangue(localStorage.getItem('polycode_app_lang') || 'fr');
    
    updateEditor();
});

function syncScroll() {
    // On synchronise parfaitement les deux couches
    highlightLayer.scrollTop = editor.scrollTop;
    highlightLayer.scrollLeft = editor.scrollLeft;
    lineNumbers.scrollTop = editor.scrollTop;
}

// AJOUT : Cette ligne permet de cliquer "à travers" la coloration pour toucher l'éditeur
highlightLayer.style.pointerEvents = "none"; 

editor.addEventListener('input', updateEditor);
editor.addEventListener('scroll', syncScroll);

// --- 3. FONCTIONS DE TRADUCTION ET THÈME ---

// Fonction pour basculer la langue (Appelée par le clic sur le drapeau)
function basculerLangueInterface() {
    let currentLang = localStorage.getItem('polycode_app_lang') || 'fr';
    let nextLang = (currentLang === 'fr') ? 'en' : 'fr';
    appliquerLangue(nextLang);
}

function appliquerLangue(lang) {
    localStorage.setItem('polycode_app_lang', lang);
    const t = translations[lang];

    // Mise à jour des boutons par classe et ID
    if(document.querySelector('.btn-run')) document.querySelector('.btn-run').innerText = t.run;
    if(document.querySelector('.btn-clear')) document.querySelector('.btn-clear').innerText = t.clear;
    if(document.getElementById('ai-btn')) document.getElementById('ai-btn').innerText = t.ai;
    if(document.querySelector('.btn-login')) document.querySelector('.btn-login').innerText = t.auth_btn;
    if(document.getElementById('username')) document.getElementById('username').placeholder = t.placeholder;
    
    // Mise à jour du drapeau (le premier span dans header-tools)
    const flagSpan = document.querySelector('.header-tools span');
    if(flagSpan) flagSpan.innerText = t.flag;

    consoleOut.innerHTML = t.ready;
}

function toggleTheme() {
    body.classList.toggle('light-mode');
    const isLight = body.classList.contains('light-mode');
    localStorage.setItem('polycode_theme', isLight ? 'light' : 'dark');
}

// --- 4. FONCTIONS DE NAVIGATION ---
function entrerDansLeTerminal() {
    const user = document.getElementById('username').value;
    if (user === "") {
        alert("Veuillez entrer votre nom.");
        return;
    }
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('terminal-screen').style.display = 'flex';
    updateEditor(); 
}

function addCode(char) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.substring(0, start) + char + editor.value.substring(end);
    editor.focus();
    editor.selectionStart = editor.selectionEnd = start + char.length;
    updateEditor(); 
}

let currentFontSize = 16;
function changeFontSize(delta) {
    currentFontSize += delta;
    editor.style.fontSize = currentFontSize + 'px';
    highlightLayer.style.fontSize = currentFontSize + 'px';
    lineNumbers.style.fontSize = currentFontSize + 'px';
    lineNumbers.style.lineHeight = (currentFontSize * 1.5) + 'px';
    updateEditor();
}

// --- 5. MOTEUR D'EXÉCUTION ---
function colorerConsole(ligne) {
    if (!ligne) return "";
    const low = ligne.toLowerCase();
    if (low.includes("error") || low.includes("erreur") || low.includes("traceback")) {
        return `<span class="log-error">${ligne}</span>`;
    }
    if (low.includes("success") || low.includes("terminé") || low.includes("ok") || low.includes("succès")) {
        return `<span class="log-success">${ligne}</span>`;
    }
    return `<span>${ligne}</span>`;
}

function lancerCode() {
    const codeEcrit = editor.value;
    const langueCode = langSelect.value;
    const langApp = localStorage.getItem('polycode_app_lang') || 'fr';
    const sound = document.getElementById('hacker-sound'); 

    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(e => console.log("Son bloqué"));
    }

    consoleOut.innerHTML = `<span class='loading'>${translations[langApp].loading}</span>`;

    fetch('/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeEcrit, lang: langueCode })
    })
    .then(response => response.json())
    .then(data => {
        if (sound) sound.pause();

        // NOUVEAU : Gestion de Chart.js
        if (data.chart_data) {
            if (data.chart_data.labels) {
                data.chart_data.labels = data.chart_data.labels.map(l => 
                    typeof l === 'number' ? Math.round(l * 100) / 100 : l
                );
            }
            if (data.chart_data.values) {
                data.chart_data.values = data.chart_data.values.map(v => 
                    typeof v === 'number' ? Math.round(v * 100) / 100 : v
                );
            }
            document.getElementById('plot-modal').style.display = 'flex';
            const ctx = document.getElementById('polyChart').getContext('2d');

            // On nettoie l'ancien graphique
            if (window.myChart) { window.myChart.destroy(); }

            // On dessine le nouveau avec un style propre
            window.myChart = new Chart(ctx, {
                type: data.chart_data.type || 'line',
                data: {
                    labels: data.chart_data.labels,
                    datasets: [{
                        label: 'Analyse PolyCode',
                        data: data.chart_data.values,
                        borderColor: '#238636',
                        backgroundColor: 'rgba(35, 134, 54, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            ticks: { 
                                maxRotation: 0, 
                                autoSkip: true, 
                                maxTicksLimit: 10, 
                                color: '#333333', // Gris foncé pour être visible
                                font: { size: 11, weight: 'bold' } 
                            },
                            grid: { color: 'rgba(0, 0, 0, 0.1)' } // Grille légère noire
                        },
                        y: { 
                            beginAtZero: true,
                            ticks: { color: '#333333' }, // Gris foncé ici aussi
                            grid: { color: 'rgba(0, 0, 0, 0.1)' } 
                        }
                    }
                }
            });
        }

        const texteBrut = data.output ? data.output.replace(/\r/g, "") : "";
        const sortieHighLight = texteBrut.split('\n').map(l => `> ${colorerConsole(l)}`).join('<br>');
        consoleOut.innerHTML = sortieHighLight;
        setTimeout(() => { consoleOut.scrollTop = consoleOut.scrollHeight; }, 50);
    })
    .catch(error => {
        if (sound) sound.pause();
        consoleOut.innerHTML = "<span class='log-error'>ERREUR: Connexion au serveur impossible.</span>";
    });
}

// --- 6. AUTRES FONCTIONS (IA & GRAPHIQUES) ---
function demanderAideIA() {
    const codeActuel = editor.value;
    const langue = langSelect.value;
    const langApp = localStorage.getItem('polycode_app_lang') || 'fr';
    
    consoleOut.innerHTML = `<span class='loading' style='color: #fbbf24;'>${translations[langApp].ia_thinking}</span>`;

    fetch('/aide_ia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeActuel, lang: langue, error: consoleOut.innerText })
    })
    .then(response => response.json())
    .then(data => {
        consoleOut.innerHTML = "<span style='color: #fbbf24;'>🤖 IA : </span>" + data.conseil;
    });
}

function fermerGraphique() {
    document.getElementById('plot-modal').style.display = 'none';
}

function telechargerGraphique() {
    const canvas = document.getElementById('polyChart');
    
    // Convertir le dessin en image
    const imageData = canvas.toDataURL("image/png");
    
    // Créer un lien de téléchargement invisible
    const lien = document.createElement('a');
    lien.href = imageData;
    lien.download = 'graphique_polycode.png';
    document.body.appendChild(lien);
    lien.click();
    document.body.removeChild(lien);

    afficherNotification("💾 Graphique enregistré dans vos téléchargements !");
}

function afficherNotification(message) {
    const note = document.createElement('div');
    note.innerText = message;
    note.style = `
        position: fixed; bottom: 20px; left: 50%; 
        transform: translateX(-50%); background: #10b981; 
        color: white; padding: 12px 25px; border-radius: 30px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 10000;
        font-family: sans-serif; transition: opacity 0.5s;
    `;
    document.body.appendChild(note);
    
    // Disparaît après 3 secondes
    setTimeout(() => {
        note.style.opacity = '0';
        setTimeout(() => note.remove(), 500);
    }, 3000);
}

function effacerConsole() {
    const langApp = localStorage.getItem('polycode_app_lang') || 'fr';
    consoleOut.innerHTML = translations[langApp].ready;
}