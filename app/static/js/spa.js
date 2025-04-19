// app/static/js/spa.js
document.addEventListener("DOMContentLoaded", () => {
    const main = document.getElementById("content");

    // Перехват всех внутренних переходов
    document.body.addEventListener("click", async (e) => {
        const link = e.target.closest("a[data-link]");
        if (link) {
            e.preventDefault();
            const url = link.getAttribute("href");
            await navigateTo(url);
        }
    });

    window.addEventListener("popstate", () => {
        loadPage(location.pathname);
    });

    async function navigateTo(url) {
        history.pushState(null, null, url);
        await loadPage(url);
    }

    async function loadPage(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Page not found");

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newContent = doc.querySelector("main") || doc.body;

            main.innerHTML = newContent.innerHTML;
            window.scrollTo(0, 0);
        } catch (err) {
            console.error("Ошибка загрузки страницы:", err);
            main.innerHTML = "<p>Ошибка загрузки страницы.</p>";
        }
    }

    // Начальная загрузка
    loadPage(location.pathname);
});
