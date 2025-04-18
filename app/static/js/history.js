// static/js/history.js

console.log("Scripts connected..")


window.addEventListener('DOMContentLoaded', () => {
    // При первом запуске pushState, чтобы не выйти сразу из приложения
 
    if (!window.history.state) {
        history.replaceState({ page: "home" }, "", window.location.pathname);
    }

    // Пример: если пользователь нажимает "назад"
    window.addEventListener("popstate", (e) => {
        if (!e.state || e.state.page === "home") {
            // Закрыть приложение (если Telegram поддерживает)
            if (window.Telegram.WebApp) {
                window.Telegram.WebApp.close();
            } else {
                // Фолбэк
                alert("Выход из приложения");
            }
        }
    });
});

// function navigateTo(event, url) {
//     event.preventDefault();
//     history.pushState({ page: url }, "", url);
//     window.location.assign(url);
// }

function navigateTo(event, url) {
    event.preventDefault();
    history.pushState({ page: url }, "", url);

    fetch(url)
        .then(res => res.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const content = doc.body.innerHTML;

            document.body.innerHTML = content;
            window.scrollTo(0, 0); // сбросить скролл вверх
        })
        .catch(err => console.error('Ошибка загрузки страницы:', err));
}
