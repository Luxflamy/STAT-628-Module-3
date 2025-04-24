import { handleFlightData, displayError } from './output.js';

export function collectFlightData() {
    const panel = document.querySelector('.input-panel');
    
    if (panel && !document.getElementById('extreme-weather')) {
        const weatherFormGroup = document.createElement('div');
        weatherFormGroup.className = 'form-group';
        weatherFormGroup.innerHTML = `
            <label class="weather-toggle">
                <input type="checkbox" id="extreme-weather">
                <span class="weather-toggle-slider"></span>
                <span class="weather-toggle-label">Extreme Weather</span>
            </label>
        `;
        
        const searchBtn = document.querySelector('#search-btn');
        if (searchBtn) {
            panel.insertBefore(weatherFormGroup, searchBtn);
        } else {
            panel.appendChild(weatherFormGroup);
        }
    }
    
    if (panel && !document.getElementById('rainfall-slider')) {
        const rainfallFormGroup = document.createElement('div');
        rainfallFormGroup.className = 'form-group rainfall-slider-container';
        rainfallFormGroup.innerHTML = `
            <label for="rainfall-slider"> Precipitaion (0-200 mm):</label>
            <div class="rainfall-slider-wrapper">
                <input type="range" id="rainfall-slider" class="rainfall-slider" min="0" max="200" value="0" step="1">
                <span id="rainfall-value" class="rainfall-slider-value">0 mm</span>
            </div>
        `;
        
        const searchBtn = document.querySelector('#search-btn');
        if (searchBtn) {
            panel.insertBefore(rainfallFormGroup, searchBtn);
            
            const rainfallSlider = document.getElementById('rainfall-slider');
            const rainfallValue = document.getElementById('rainfall-value');
            
            if (rainfallSlider && rainfallValue) {
                rainfallSlider.addEventListener('input', function() {
                    rainfallValue.textContent = this.value + ' mm';
                });
            }
        } else {
            panel.appendChild(rainfallFormGroup);
        }
    }

    const fromInput = document.querySelector('#from');
    const toInput = document.querySelector('#to');
    const timeInput = document.querySelector('#time');
    const flightNumberInput = document.querySelector('#flight-number');
    const searchButton = document.querySelector('#search-btn');

    const newSearchBtn = searchButton.cloneNode(true);
    if (searchButton.parentNode) {
        searchButton.parentNode.replaceChild(newSearchBtn, searchButton);
    }

    newSearchBtn.addEventListener('click', async () => {
        const extremeWeatherInput = document.querySelector('#extreme-weather');
        const extremeWeather = extremeWeatherInput ? extremeWeatherInput.checked ? 1 : 0 : 0;
        
        const rainfallSlider = document.querySelector('#rainfall-slider');
        const rainfall = rainfallSlider ? parseFloat(rainfallSlider.value) : 0;
        
        const from = fromInput.value.trim().toUpperCase();
        const to = toInput.value.trim().toUpperCase();
        const time = timeInput.value;
        const flightNumber = flightNumberInput.value.trim().toUpperCase();
        
        const airline = flightNumber.substring(0, 2);
        
        let depTime = 0;
        let year = 0;
        let week = 0;
        
        if (time) {
            const date = new Date(time);
            
            const hours = date.getHours();
            const minutes = date.getMinutes();
            depTime = hours * 100 + minutes;
            
            year = date.getFullYear();
            
            week = date.getDay();
        }
        
        const distance = 0;
        
        const flightData = {
            from,
            to,
            time,
            flightNumber,
            airline,
            depTime,
            year,
            week,
            distance,
            extremeWeather,
            rainfall
        };

        handleFlightData(flightData);

        try {
            const response = await fetch('http://127.0.0.1:5000/run-python', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: `${flightData.from},${flightData.to}` })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            let displayPanel = document.querySelector('.display-panel');
            if (!displayPanel) {
                displayPanel = document.createElement('div');
                displayPanel.classList.add('display-panel');
                document.body.appendChild(displayPanel);
                void displayPanel.offsetWidth;
            }

            displayPanel.style.width = '80%';
            displayPanel.style.margin = '0 auto';
            displayPanel.style.maxWidth = '1200px';

            const predictionResponse = await fetch('http://127.0.0.1:5000/predict-cancellation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flightData })
            });

            if (!predictionResponse.ok) {
                throw new Error(`HTTP error! status: ${predictionResponse.status}`);
            }

            const predictionResult = await predictionResponse.json();
            
            handleFlightData(flightData, predictionResult, displayPanel);
            
        } catch (error) {
            console.error('Error calling Python script:', error);
            displayError(error.message);
        }
    });
}

