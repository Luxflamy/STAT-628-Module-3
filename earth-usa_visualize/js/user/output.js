let isCardExpanded = false;

export function handleFlightData(flightData, predictionResult = null, displayPanel = null) {
    console.log('Collected Flight Data:', flightData);

    if (!displayPanel) {
        displayPanel = document.querySelector('.display-panel');
        if (!displayPanel) {
            displayPanel = document.createElement('div');
            displayPanel.classList.add('display-panel');
            displayPanel.style.width = '80%';
            displayPanel.style.margin = '0 auto';
            displayPanel.style.maxWidth = '1200px';
            document.body.appendChild(displayPanel);
            void displayPanel.offsetWidth;
        }
    }

    displayPanel.classList.add('visible');
    
    if (predictionResult) {
        displayPredictionResult(flightData, predictionResult, displayPanel);
    }
}

export function displayError(errorMessage) {
    let displayPanel = document.querySelector('.display-panel');
    if (displayPanel) {
        displayPanel.innerHTML += `
            <div class="cards-container" style="display: flex; flex-direction: row; overflow-x: auto;">
                <div class="flight-card error-card" style="flex: 0 0 auto; min-width: 350px;">
                    <h3>Error</h3>
                    <div class="flight-card-content">
                        <p>${errorMessage}</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function displayPredictionResult(flightData, predictionResult, displayPanel) {
    const existingDetails = document.querySelector('.flight-card-details');
    if (existingDetails) {
        isCardExpanded = existingDetails.style.display !== 'none' && 
                        existingDetails.style.maxHeight !== '0px';
    }

    const detailsInitialStyle = isCardExpanded 
        ? 'display: block; overflow: hidden; max-height: 1000px; padding: 10px 0 0 0;' 
        : 'display: none; overflow: hidden; max-height: 0; padding: 0;';
    
    const indicatorInitialText = isCardExpanded ? '▲ Hide details' : '▼ Show details';
    
    const cancelProb = predictionResult.cancellation_probability * 100;
    let probColor;
    let riskLevel;
    
    if (cancelProb <= 2.1) {
        probColor = '#4CAF50';
        riskLevel = "Safe";
    } else if (cancelProb <= 4) {
        probColor = '#FF9800';
        riskLevel = "At Risk";
    } else if (cancelProb <= 7) {
        probColor = '#FF5252';
        riskLevel = "High Risk";
    } else {
        probColor = '#B71C1C';
        riskLevel = "Extreme Risk";
    }

    const redEyeEmoji = predictionResult.is_redeye ? "🌙 ✈️ 😴" : "☀️";

    let formattedTime = "Time not specified";
    let dayOfWeek = "";
    if (flightData.time) {
        const date = new Date(flightData.time);
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const hour12 = hours % 12 || 12;
        const weekdayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        dayOfWeek = weekdayNames[date.getDay()];
        formattedTime = `${dayOfWeek}, ${hour12}:${minutes < 10 ? '0' + minutes : minutes} ${ampm}`;
    }

    const hasOriginDest = flightData.from && flightData.to && flightData.from !== '' && flightData.to !== '';
    const distance = hasOriginDest ? (predictionResult.model_input?.DISTANCE || 0) : 0;
    const flightHours = Math.floor(distance / 500);
    const flightMinutes = Math.round((distance / 500 - flightHours) * 60);
    const flightTimeText = !hasOriginDest ? "Data unavailable" : (
        flightHours > 0 
        ? `approx. ${flightHours} hour${flightHours > 1 ? 's' : ''}${flightMinutes > 0 ? ' ' + flightMinutes + ' min' : ''}`
        : `approx. ${flightMinutes} min`
    );

    const canShowCancelProb = hasOriginDest;
    const cancelProbDisplay = canShowCancelProb 
        ? `<span style="color: ${probColor}; font-weight: bold;">${cancelProb.toFixed(2)}%</span>
           <span style="color: ${probColor}; font-weight: bold; margin-left: auto;">${riskLevel}</span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;
    
    const canShowRedEye = flightData.time && flightData.time !== '';
    const redEyeDisplay = canShowRedEye
        ? `${predictionResult.is_redeye ? "Yes" : "No"}<span style="margin-left: auto;">${redEyeEmoji}</span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;
        
    const hasDelayPrediction = predictionResult.delay_probability !== undefined && 
                              predictionResult.predicted_delay_minutes !== undefined;
    
    let delayColor = '#4CAF50';
    let delayStatus = "On Time";
    
    if (hasDelayPrediction) {
        const delayProb = predictionResult.delay_probability * 100;
        const delayMinutes = predictionResult.predicted_delay_minutes;
        
        if (delayMinutes >= 60 || delayProb >= 50) {
            delayColor = '#B71C1C';
            delayStatus = "Significant Delay";
        } else if (delayMinutes >= 35 || delayProb >= 40) {
            delayColor = '#FF5252';
            delayStatus = "Moderate Delay";
        } else if (delayMinutes >= 15 || delayProb >= 30) {
            delayColor = '#FF9800';
            delayStatus = "Minor Delay";
        }
    }
    
    const delayProbDisplay = hasDelayPrediction 
        ? `<span style="color: ${delayColor}; font-weight: bold;">${(predictionResult.delay_probability * 100).toFixed(2)}%</span>
           <span style="color: ${delayColor}; font-weight: bold; margin-left: auto;">${delayStatus}</span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;
    
    const delayTimeDisplay = hasDelayPrediction
        ? `<span style="color: ${delayColor}; font-weight: bold;">${Math.round(predictionResult.predicted_delay_minutes)} minutes</span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;

    const hasConfidenceInterval = hasDelayPrediction && 
                                  predictionResult.delay_confidence_interval && 
                                  predictionResult.delay_confidence_interval.lower !== undefined &&
                                  predictionResult.delay_confidence_interval.upper !== undefined;
    
    const confidenceIntervalDisplay = hasConfidenceInterval
        ? `<span style="color: #666;">[${Math.round(predictionResult.delay_confidence_interval.lower)}-${Math.round(predictionResult.delay_confidence_interval.upper)} mins]</span>`
        : '';

    const hasArrivalDelayPrediction = predictionResult.arrival_delay !== undefined && 
                                     predictionResult.arrival_delay.probability !== undefined && 
                                     predictionResult.arrival_delay.minutes !== undefined;
    
    let arrDelayColor = '#4CAF50';
    let arrDelayStatus = "On Time";
    let isEarlyArrival = false;
    
    if (hasArrivalDelayPrediction) {
        const arrDelayProb = predictionResult.arrival_delay.probability * 100;
        const arrDelayMinutes = predictionResult.arrival_delay.minutes;
        
        if (arrDelayMinutes <= 0) {
            arrDelayColor = '#4CAF50';
            arrDelayStatus = "Early Arrival";
            isEarlyArrival = true;
        } else if (arrDelayMinutes >= 60 || arrDelayProb >= 50) {
            arrDelayColor = '#B71C1C';
            arrDelayStatus = "Significant Delay";
        } else if (arrDelayMinutes >= 35 || arrDelayProb >= 40) {
            arrDelayColor = '#FF5252';
            arrDelayStatus = "Moderate Delay";
        } else if (arrDelayMinutes >= 15 || arrDelayProb >= 30) {
            arrDelayColor = '#FF9800';
            arrDelayStatus = "Minor Delay";
        }
    }
    
    const arrDelayProbDisplay = hasArrivalDelayPrediction 
        ? `<span style="color: ${arrDelayColor}; font-weight: bold;">${(predictionResult.arrival_delay.probability * 100).toFixed(2)}%</span>
           <span style="color: ${arrDelayColor}; font-weight: bold; margin-left: auto;">${arrDelayStatus}</span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;
    
    const arrDelayTimeDisplay = hasArrivalDelayPrediction
        ? `<span style="color: ${arrDelayColor}; font-weight: bold;">
            ${isEarlyArrival 
                ? `${Math.abs(Math.round(predictionResult.arrival_delay.minutes))} minutes early` 
                : `${Math.round(predictionResult.arrival_delay.minutes)} minutes`}
           </span>`
        : `<span style="color: #888; font-style: italic;">Data unavailable</span>`;

    const hasArrConfidenceInterval = hasArrivalDelayPrediction && 
                                   predictionResult.arrival_delay.confidence_interval &&
                                   predictionResult.arrival_delay.confidence_interval.lower !== undefined &&
                                   predictionResult.arrival_delay.confidence_interval.upper !== undefined;
    
    const arrConfidenceIntervalDisplay = hasArrConfidenceInterval
        ? `<span style="color: #666;">${isEarlyArrival
            ? `[${Math.abs(Math.round(predictionResult.arrival_delay.confidence_interval.upper))}-${Math.abs(Math.round(predictionResult.arrival_delay.confidence_interval.lower))} mins early]`
            : `[${Math.round(predictionResult.arrival_delay.confidence_interval.lower)}-${Math.round(predictionResult.arrival_delay.confidence_interval.upper)} mins]`
          }</span>`
        : '';

    displayPanel.innerHTML = `
        <div class="cards-container" style="display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 20px; padding: 10px 0;">
            <div class="flight-card" style="flex: 0 0 auto;">
                <h3>Flight Prediction</h3>
                <div class="flight-card-content">
                    <p style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>Cancellation Probability:</strong>&nbsp;&nbsp;
                        ${cancelProbDisplay}
                    </p>
                    <p style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>Dep-Delay Prob:</strong>&nbsp;&nbsp;
                        ${delayProbDisplay}
                    </p>
                    <p style="display: flex; align-items: center;">
                        <strong>Expected Dep-Delay:</strong>&nbsp;
                        <span style="margin-right: auto;">${delayTimeDisplay}</span>
                        <span>${confidenceIntervalDisplay}</span>
                    </p>
                    <p style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>Arr-Delay Prob:</strong>&nbsp;&nbsp;
                        ${arrDelayProbDisplay}
                    </p>
                    <p style="display: flex; align-items: center;">
                        <strong>${isEarlyArrival ? 'Expected Early Arrival:' : 'Expected Arr-Delay:'}</strong>&nbsp;
                        <span style="margin-right: auto;">${arrDelayTimeDisplay}</span>
                        <span>${arrConfidenceIntervalDisplay}</span>
                    </p>
                    <p style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>Red-eye Flight:</strong>&nbsp;&nbsp; ${redEyeDisplay}
                    </p>
                    <p><strong>Departure Time:</strong> ${formattedTime}</p>
                    <p><strong>Distance:</strong> ${hasOriginDest ? `${distance} miles` : "Data unavailable"}</p>
                    <p><strong>Est. Flight Duration:</strong> ${flightTimeText}</p>
                </div>
                <div class="flight-card-details" style="${detailsInitialStyle} transition: max-height 0.6s ease-in-out, padding 0.6s ease-in-out;">
                    <p><strong>Extreme Weather:</strong> ${predictionResult.model_input?.EXTREME_WEATHER ? "Yes" : "No"}</p>
                    <p><strong>Rainfall:</strong> ${predictionResult.model_input?.PRCP} mm</p>
                    ${predictionResult.error ? `<p class="error"><strong>Error:</strong> ${predictionResult.error}</p>` : ''}
                    <div class="model-input-data">
                        <p><strong>YEAR:</strong> ${predictionResult.model_input?.YEAR || flightData.year}</p>
                        <p><strong>WEEK:</strong> ${predictionResult.model_input?.WEEK || flightData.week}</p>
                        <p><strong>MKT_AIRLINE:</strong> ${predictionResult.model_input?.MKT_AIRLINE || flightData.airline}</p>
                        <p><strong>ORIGIN_IATA:</strong> ${predictionResult.model_input?.ORIGIN_IATA || flightData.from}</p>
                        <p><strong>DEST_IATA:</strong> ${predictionResult.model_input?.DEST_IATA || flightData.to}</p>
                        <p><strong>DISTANCE:</strong> ${predictionResult.model_input?.DISTANCE !== undefined ? predictionResult.model_input.DISTANCE : '1 (default)'}</p>
                        <p><strong>DEP_TIME:</strong> ${predictionResult.model_input?.DEP_TIME || flightData.depTime}</p>
                        <p><strong>IS_REDEYE:</strong> ${predictionResult.model_input?.IS_REDEYE !== undefined ? predictionResult.model_input.IS_REDEYE : 'Not provided'}</p>
                        <p><strong>PRCP:</strong> ${predictionResult.model_input?.PRCP !== undefined ? predictionResult.model_input.PRCP : '0 (default)'}</p>
                        <p><strong>EX_WEATHER:</strong> ${predictionResult.model_input?.EXTREME_WEATHER !== undefined ? predictionResult.model_input.EXTREME_WEATHER : '0 (default)'}</p>
                    </div>
                </div>
                <div class="expand-indicator" style="text-align: center; cursor: pointer; padding: 5px 0; font-size: 12px;">
                    <span>${indicatorInitialText}</span>
                </div>
            </div>
            
            <div class="flight-card travel-tips-card" style="flex: 0 0 auto;">
                <h3>Travel Tips</h3>
                <div class="flight-card-content">
                    ${cancelProb > 3 ? 
                        `<div class="travel-alert">
                            <p><strong>⚠️ High Cancellation Risk Alert</strong></p>
                            <p>Based on our prediction, this flight has an elevated risk of cancellation.</p>
                        </div>` : ''
                    }
                    ${hasDelayPrediction && predictionResult.predicted_delay_minutes > 20 ? 
                        `<div class="travel-alert" style="margin-top: ${cancelProb > 3 ? '10px' : '0'}">
                            <p><strong>⏱️ Departure Delay Alert</strong></p>
                            <p>This flight has a significant chance of delayed departure by about ${Math.round(predictionResult.predicted_delay_minutes)} minutes.</p>
                        </div>` : ''
                    }
                    ${hasArrivalDelayPrediction && !isEarlyArrival && predictionResult.arrival_delay.minutes > 25 ? 
                        `<div class="travel-alert" style="margin-top: ${(cancelProb > 3 || (hasDelayPrediction && predictionResult.predicted_delay_minutes > 20)) ? '10px' : '0'}">
                            <p><strong>⏱️ Arrival Delay Alert</strong></p>
                            <p>This flight is predicted to arrive about ${Math.round(predictionResult.arrival_delay.minutes)} minutes late at destination.</p>
                        </div>` : ''
                    }
                    ${hasArrivalDelayPrediction && isEarlyArrival && Math.abs(predictionResult.arrival_delay.minutes) > 10 ? 
                        `<div class="travel-alert" style="margin-top: ${(cancelProb > 3 || (hasDelayPrediction && predictionResult.predicted_delay_minutes > 20)) ? '10px' : '0'};">
                            <p><strong>✅ Early Arrival Expected</strong></p>
                            <p>Good news! This flight is predicted to arrive about ${Math.abs(Math.round(predictionResult.arrival_delay.minutes))} minutes early at destination.</p>
                        </div>` : ''
                    }
                    <h4>Recommended Actions:</h4>
                    <ul>
                        ${hasOriginDest ? 
                            `<li>Arrive at ${flightData.from} airport at least ${distance > 1000 ? '3' : '2'} hours before departure.</li>` : 
                            '<li>Arrive at the airport with plenty of time before departure.</li>'
                        }
                        <li>Download the airline's app for real-time flight updates.</li>
                        ${predictionResult.model_input?.EXTREME_WEATHER ? 
                            '<li><strong>Weather Warning:</strong> Check airport conditions due to forecasted extreme weather.</li>' : 
                            '<li>Monitor current weather conditions at departure and arrival cities.</li>'
                        }
                        ${predictionResult.model_input?.PRCP > 50 ? 
                            '<li><strong>Precipitation Alert:</strong> Heavy rainfall may cause delays. Consider flexibility in your travel plans.</li>' : 
                            ''
                        }
                        ${predictionResult.is_redeye ? 
                            '<li>For this red-eye flight, consider bringing items for comfort (neck pillow, eye mask, etc).</li>' : 
                            ''
                        }
                        ${hasDelayPrediction && predictionResult.predicted_delay_minutes > 30 ? 
                            '<li>Consider bringing snacks and entertainment as significant delays are expected.</li>' : 
                            ''
                        }
                    </ul>
                    
                    <h4>Alternative Options:</h4>
                    <ul>
                        ${cancelProb > 4 ? 
                            '<li><strong>Consider booking a backup flight</strong> if your travel is time-sensitive.</li>' : 
                            ''
                        }
                        ${hasDelayPrediction && predictionResult.predicted_delay_minutes > 45 ? 
                            '<li><strong>Check for alternative flights</strong> as this flight may experience significant departure delays.</li>' : 
                            ''
                        }
                        ${hasArrivalDelayPrediction && !isEarlyArrival && predictionResult.arrival_delay.minutes > 60 ? 
                            '<li><strong>Consider earlier flights</strong> as this flight may arrive significantly delayed.</li>' : 
                            ''
                        }
                        <li>Check refund and rebooking policies for your ticket.</li>
                        <li>Consider travel insurance for important trips.</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    const flightCard = displayPanel.querySelector('.flight-card');
    const detailsSection = displayPanel.querySelector('.flight-card-details');
    const expandIndicator = displayPanel.querySelector('.expand-indicator');
    
    expandIndicator.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDetails();
    });
    
    flightCard.addEventListener('click', (e) => {
        if (e.target.closest('.expand-indicator')) return;
        toggleDetails();
    });
    
    function toggleDetails() {
        isCardExpanded = !isCardExpanded;
        updateCardExpandState();
    }
    
    function updateCardExpandState() {
        if (isCardExpanded) {
            detailsSection.style.display = 'block';
            void detailsSection.offsetHeight;
            detailsSection.style.maxHeight = '1000px';
            detailsSection.style.padding = '10px 0 0 0';
            expandIndicator.innerHTML = '<span>▲ Hide details</span>';
        } else {
            detailsSection.style.maxHeight = '0';
            detailsSection.style.padding = '0';
            expandIndicator.innerHTML = '<span>▼ Show details</span>';
            setTimeout(() => {
                detailsSection.style.display = 'none';
            }, 600);
        }
    }
}
