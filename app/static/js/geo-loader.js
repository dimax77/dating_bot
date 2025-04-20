document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('country');
    const citySelect = document.getElementById('city');

    const RAPID_API_KEY = 'YOUR_REAL_API_KEY_HERE';  // вставь сюда ключ
    const RAPID_API_HOST = 'wft-geo-db.p.rapidapi.com';

    // Загрузка стран
    fetch('https://restcountries.com/v3.1/all')
        .then(res => res.json())
        .then(data => {
            data.sort((a, b) => a.name.common.localeCompare(b.name.common));
            data.forEach(country => {
                const option = document.createElement('option');
                option.value = country.cca2;
                option.textContent = country.name.common;
                countrySelect.appendChild(option);
            });
        });

    // При выборе страны загружаем города
    countrySelect.addEventListener('change', () => {
        const countryCode = countrySelect.value;
        citySelect.innerHTML = '<option>Loading...</option>';

        fetch(`https://wft-geo-db.p.rapidapi.com/v1/geo/countries/${countryCode}/cities?limit=20&sort=-population`, {
            method: 'GET',
            headers: {
                'X-RapidAPI-Key': RAPID_API_KEY,
                'X-RapidAPI-Host': RAPID_API_HOST
            }
        })
            .then(response => response.json())
            .then(data => {
                citySelect.innerHTML = '';
                data.data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.name;
                    option.textContent = city.name;
                    citySelect.appendChild(option);
                });
            })
            .catch(err => {
                console.error('Error loading cities:', err);
                citySelect.innerHTML = '<option>Error loading</option>';
            });
    });
});
