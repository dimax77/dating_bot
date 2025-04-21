// app/static/js/spa.js

const STORAGE_KEY = 'navStack';
let navStack = JSON.parse(sessionStorage.getItem(STORAGE_KEY)) || [];
let currentPath = location.pathname + location.search;

// Telegram WebApp готов
Telegram.WebApp.ready();
Telegram.WebApp.expand();

const tgUser = Telegram.WebApp.initDataUnsafe.user;

if (tgUser && tgUser.id && !sessionStorage.getItem("auth_done")) {
    fetch("/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: tgUser.id })
    }).then(() => {
        // Перезагрузим, чтобы отобразилось правильное содержимое
        sessionStorage.setItem("auth_done", "1");

        location.reload();
    });
}

// Обновление состояния кнопки "Назад"
function updateBackButton() {
    if (navStack.length > 0) {
        Telegram.WebApp.BackButton.show();
    } else {
        Telegram.WebApp.BackButton.hide();
    }
}

// Сохранение навигационного стека
function persistStack() {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(navStack));
}

// Показ/скрытие прелоадера
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'block';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'none';
}

// Загрузка и отображение страницы
async function loadPage(url) {
    console.log("Requsted URL: ", url)
    showLoader();
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Page not found");

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newContent = doc.querySelector("main") || doc.body;

        document.getElementById("content").innerHTML = newContent.innerHTML;
        window.scrollTo(0, 0);
    } catch (err) {
        console.error("Ошибка загрузки страницы:", err);
        document.getElementById("content").innerHTML = "<p>Ошибка загрузки страницы.</p>";
    } finally {
        hideLoader();
    }
}

// Навигация по ссылке
async function navigateTo(url) {
    if (url !== currentPath) {
        navStack.push(currentPath);
        currentPath = url;
        history.pushState(null, null, url);
        await loadPage(url);
        if (window.location.pathname.startsWith("/create-profile")) {
            console.log("GOT YA! Window.LocationPathname: ", window.location.pathname)

            import("/static/js/geo-loader.js").then(({ initGeoLoader }) => {
                // setTimeout(() => initGeoLoader(), 10);
                setTimeout(() => {
                    if (document.getElementById("country")) {
                        initGeoLoader();
                    } else {
                        console.warn("Элемент country не найден при initGeoLoader");
                    }
                }, 0);
            }).catch(err => {
                console.error("Failed to load geo-loader:", err);
            });
        }
        persistStack();
        updateBackButton();
    }
}

// Обработка кнопки "Назад" Telegram
Telegram.WebApp.BackButton.onClick(() => {
    if (navStack.length > 0) {
        const prevUrl = navStack.pop();
        currentPath = prevUrl;
        history.pushState(null, null, prevUrl);
        loadPage(prevUrl);
        persistStack();
        updateBackButton();
    } else {
        Telegram.WebApp.close();
    }
});

// DOM загружен
document.addEventListener("DOMContentLoaded", () => {
    const main = document.getElementById("content");

    // Перехват всех внутренних переходов по ссылкам
    document.body.addEventListener("click", async (e) => {
        const link = e.target.closest("a[data-link]");
        if (link) {
            e.preventDefault();
            const url = link.getAttribute("href");
            await navigateTo(url);
        }
    });

    // Обработка кнопки "Назад" браузера
    window.addEventListener("popstate", () => {
        currentPath = location.pathname + location.search;
        loadPage(currentPath);
        updateBackButton();
    });

    // Обработка отправки формы профиля
    document.addEventListener("submit", async (e) => {
        const form = e.target;
        if (form.id === "profileForm") {
            e.preventDefault();

            const formData = new FormData(form);
            try {
                const response = await fetch("/create_profile", {
                    method: "POST",
                    body: formData,
                });

                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const newContent = doc.querySelector("main");

                main.innerHTML = newContent.innerHTML;

                const url = "/";
                history.pushState(null, null, url);
                currentPath = url;
                window.scrollTo(0, 0);
            } catch (err) {
                console.error("Ошибка при создании анкеты:", err);
            }
        }
    });

    // Инициализация
    loadPage(currentPath);
    updateBackButton();
});
