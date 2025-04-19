// app/static/js/history.js

console.log("Scripts connected..")


window.addEventListener('DOMContentLoaded', () => {
 
    if (!window.history.state) {
        history.replaceState({ page: "home" }, "", window.location.pathname);
    }

    window.addEventListener("popstate", (e) => {
        if (!e.state || e.state.page === "home") {
            if (window.Telegram.WebApp) {
                window.Telegram.WebApp.close();
            } else {
                alert("Выход из приложения");
            }
        }
    });
});

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
            window.scrollTo(0, 0);
        })
        .catch(err => console.error('Ошибка загрузки страницы:', err));
}
