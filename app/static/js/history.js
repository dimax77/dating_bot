// static/js/history.js

console.log("Scripts connected..")


window.addEventListener('DOMContentLoaded', () => {
    // При первом запуске pushState, чтобы не выйти сразу из приложения
    if (!window.location.hash) {
        history.replaceState({ page: "home" }, "", window.location.pathname + "#home");
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

function navigateTo(event, url) {
    event.preventDefault();
    history.pushState({ page: url }, "", url);
    window.location.href = url;
}