// app/static/js/geo-loader.js

document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('country');
    const citySelect = document.getElementById('city');
    const photoInput = document.getElementById('photo');
    const preview = document.getElementById('photo-preview');

    // Fetch country list on page load
    fetch('https://countriesnow.space/api/v0.1/countries/positions')
        .then(res => res.json())
        .then(data => {
            const countries = data.data;
            countries.sort((a, b) => a.name.localeCompare(b.name));
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country.name;
                option.textContent = country.name;
                countrySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Failed to load country list:', error);
        });

    // Load cities when a country is selected
    countrySelect.addEventListener('change', () => {
        const selectedCountry = countrySelect.value;
        citySelect.innerHTML = '<option>Loading...</option>';

        if (selectedCountry) {
            fetch('https://countriesnow.space/api/v0.1/countries/cities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ country: selectedCountry })
            })
                .then(res => res.json())
                .then(data => {
                    citySelect.innerHTML = ''; // Clear existing options
                    data.data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city;
                        option.textContent = city;
                        citySelect.appendChild(option);
                    });
                    citySelect.disabled = false; // Enable city dropdown after fetching cities
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
