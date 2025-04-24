/**
 * 3D Earth Visualization - Main Program (sketch.js)
 * Functionality: Create a 3D Earth with country/state boundaries, supporting mouse interaction for rotation
 */
import { iataToCoordinates } from './geoDataLoader.js';
import { initScene, initCamera, initRenderer, initLighting, scene, camera, renderer } from './sceneSetup.js';
import { initEarth, earth } from './earthModel.js';
import { loadGeoJSON, loadAirports } from './geoDataLoader.js';
import { initEventListeners, targetRotation, isDragging, previousMousePosition } from './eventHandlers.js';
import { animate } from './animationLoop.js';
import { createDust } from './dustEffect.js';
import { showLoadingScreen, hideLoadingScreen } from './loadingScreen.js';
import { setAirportCoordinates, startRandomFlightPaths, startFlightsFromAirport, startFlightsToAirport, startFlightsFromToAirport, setFromAirportCoordinates, setToAirportCoordinates, clearAllFlights } from './flightPathRenderer.js';
import { createInputPanel } from './ui/inputPanel.js';

const EARTH_RADIUS = 1;
const BORDER_OFFSET = 0.001;
const ROTATION_SPEED = 0.00005; // Adjust this value to change the rotation speed

let particles;
let globalRotation = { y: 0 };
let currentRotation = { x: 0, y: 0 };

function init() {
    showLoadingScreen(); // Display the loading screen

    initScene();
    initCamera();
    initRenderer();
    initLighting();
    initEarth(scene, EARTH_RADIUS, BORDER_OFFSET);
    
    // Create input panel
    const panel = createInputPanel();

    // Load geographic data
    Promise.all([
        loadGeoJSON('assets/countries.geojson', 0x888888, 1, earth, EARTH_RADIUS, BORDER_OFFSET),
        loadGeoJSON('assets/us-states.geojson', 0x2596be, 4, earth, EARTH_RADIUS, BORDER_OFFSET),
        loadAirports('assets/airports.geojson', earth, EARTH_RADIUS, BORDER_OFFSET) // Load airport data
            .then(airportCoordinates => {
                // Set airport coordinates
                setAirportCoordinates(airportCoordinates);
            })
    ]).then(() => {
        // Ensure all resources are loaded before hiding the loading screen
        hideLoadingScreen();

        // Get input panel values
        const fromInput = panel.querySelector('#from');
        const toInput = panel.querySelector('#to');
        const searchButton = panel.querySelector('#search-btn');
        let flightInterval = null;
        startRandomFlightPaths(earth, EARTH_RADIUS, BORDER_OFFSET);
        searchButton.addEventListener('click', () => {
            // Clear previous flight path generation logic
            if (flightInterval) {
                clearInterval(flightInterval);
            }

            // Remove previous flight paths
            clearAllFlights(earth);

            const fromCode = fromInput.value.trim().toUpperCase();
            const toCode = toInput.value.trim().toUpperCase();

            if (fromCode && iataToCoordinates[fromCode]) {
                const fromCoordinates = iataToCoordinates[fromCode];
                setFromAirportCoordinates(fromCoordinates);

                if (toCode && iataToCoordinates[toCode]) {
                    // From a specific airport to a specific airport
                    const toCoordinates = iataToCoordinates[toCode];
                    setToAirportCoordinates(toCoordinates);
                    startFlightsFromToAirport(earth, EARTH_RADIUS, BORDER_OFFSET);
                } else {
                    // From a specific airport to random airports
                    startFlightsFromAirport(earth, EARTH_RADIUS, BORDER_OFFSET);
                }
            } else if (toCode && iataToCoordinates[toCode]) {
                // To a specific airport
                const toCoordinates = iataToCoordinates[toCode];
                setToAirportCoordinates(toCoordinates);
                startFlightsToAirport(earth, EARTH_RADIUS, BORDER_OFFSET);
            }
        });
    });

    initEventListeners(camera, renderer);
    particles = createDust(earth);
}

init();
animate(renderer, scene, camera, earth, particles, globalRotation, targetRotation, currentRotation, ROTATION_SPEED);