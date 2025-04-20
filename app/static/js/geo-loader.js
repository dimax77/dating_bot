// app/static/js/geo-loader.js

console.log("GEO JS LOADED");

document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('country');
    const citySelect = document.getElementById('city');
    const photoInput = document.getElementById('photo');
    const preview = document.getElementById('photo-preview');


    fetch('/geo/countries')
        .then(res => res.json())
        .then(countries => {
            console.log('Countries received:', countries);

            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countrySelect.appendChild(option);
            });
        })
        .catch(error => console.error('Failed to load country list:', error));

    countrySelect.addEventListener('change', () => {
        const selectedCountry = countrySelect.value;
        citySelect.innerHTML = '<option>Loading...</option>';

        if (selectedCountry) {
            fetch(`/geo/cities/${encodeURIComponent(selectedCountry)}`)
                .then(res => res.json())
                .then(cities => {
                    citySelect.innerHTML = '';
                    cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city;
                        option.textContent = city;
                        citySelect.appendChild(option);
                    });
                    citySelect.disabled = false;
                })
                .catch(err => {
                    console.error('Error loading cities:', err);
                    citySelect.innerHTML = '<option>Error loading cities</option>';
                    citySelect.disabled = true;
                });
        }
    });


    // Photo preview logic
    photoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (evt) => {
                preview.src = evt.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
});
