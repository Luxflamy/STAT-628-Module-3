import { latLongToVector3 } from './earthModel.js';

let activeFlights = []; // Store all active flight paths

export function createFlightPath(startLat, startLon, endLat, endLon, earth, EARTH_RADIUS, BORDER_OFFSET) {
    const start = latLongToVector3(startLat, startLon, EARTH_RADIUS + BORDER_OFFSET);
    const end = latLongToVector3(endLat, endLon, EARTH_RADIUS + BORDER_OFFSET);

    const curve = new THREE.QuadraticBezierCurve3(
        start,
        start.clone().add(end).multiplyScalar(0.5).setLength(EARTH_RADIUS + BORDER_OFFSET + 0.1),
        end
    );

    const points = curve.getPoints(50);
    const geometry = new THREE.BufferGeometry().setFromPoints(points);

    const material = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            color: { value: new THREE.Color(0xff6361) },
            glowColor: { value: new THREE.Color(0xff8080) }
        },
        vertexShader: `
            varying vec3 vPosition;
            void main() {
                vPosition = position;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 color;
            uniform vec3 glowColor;
            uniform float time;
            varying vec3 vPosition;
            
            void main() {
                float glow = sin(time * 3.0) * 0.5 + 0.5;
                vec3 finalColor = mix(color, glowColor, glow);
                gl_FragColor = vec4(finalColor, 1.0);
            }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    const line = new THREE.Line(geometry, material);
    earth.add(line);

    activeFlights.push(line);

    const glowMaterial = new THREE.LineBasicMaterial({
        color: 0xff8080,
        transparent: true,
        opacity: 0.3,
        blending: THREE.AdditiveBlending,
        linewidth: 2
    });

    const glowLine = new THREE.Line(geometry.clone(), glowMaterial);
    earth.add(glowLine);

    activeFlights.push(glowLine);

    animateFlight(line, glowLine, points, earth, EARTH_RADIUS, BORDER_OFFSET, endLat, endLon);
}

function animateFlight(line, glowLine, points, earth, EARTH_RADIUS, BORDER_OFFSET, endLat, endLon) {
    const totalPoints = points.length;
    let currentPoint = 0;
    let time = 0;

    function animate() {
        if (currentPoint < totalPoints) {
            const visiblePoints = points.slice(0, currentPoint + 1);
            line.geometry.setFromPoints(visiblePoints);
            glowLine.geometry.setFromPoints(visiblePoints);
            
            time += 0.1;
            line.material.uniforms.time.value = time;
            
            currentPoint++;
            requestAnimationFrame(animate);
        } else {
            createFlashingRing(endLat, endLon, earth, EARTH_RADIUS, BORDER_OFFSET);
            fadeOutFlight(line, glowLine, points, earth);
        }
    }

    animate();
}

function fadeOutFlight(line, glowLine, points, earth) {
    let currentPoint = points.length;
    let opacity = 1;

    function animateFadeOut() {
        if (currentPoint > 0) {
            const visiblePoints = points.slice(points.length - currentPoint);
            line.geometry.setFromPoints(visiblePoints);
            glowLine.geometry.setFromPoints(visiblePoints);
            
            opacity -= 0.02;
            glowLine.material.opacity = opacity * 0.3;
            
            currentPoint--;
            requestAnimationFrame(animateFadeOut);
        } else {
            earth.remove(line);
            earth.remove(glowLine);
        }
    }

    animateFadeOut();
}

function createFlashingRing(lat, lon, earth, EARTH_RADIUS, BORDER_OFFSET) {
    const textureLoader = new THREE.TextureLoader();
    const ringTexture = textureLoader.load('assets/Red Ellipse.png');

    const material = new THREE.SpriteMaterial({
        map: ringTexture,
        transparent: true,
        opacity: 0.8
    });

    const sprite = new THREE.Sprite(material);
    const position = latLongToVector3(lat, lon, EARTH_RADIUS + BORDER_OFFSET + 0.001);
    sprite.position.copy(position);

    const scale = 0.04;
    sprite.scale.set(scale, scale, 1);
    earth.add(sprite);

    let growing = true;
    const maxScale = 0.06;
    const minScale = 0.01;

    function animateRing() {
        if (growing) {
            sprite.scale.x += 0.0005;
            sprite.scale.y += 0.0005;
            if (sprite.scale.x >= maxScale) growing = false;
        } else {
            sprite.scale.x -= 0.0005;
            sprite.scale.y -= 0.0005;
            if (sprite.scale.x <= minScale) growing = true;
        }

        sprite.material.opacity -= 0.01;
        if (sprite.material.opacity <= 0) {
            earth.remove(sprite);
        } else {
            requestAnimationFrame(animateRing);
        }
    }

    animateRing();
}

let airportCoordinates = [];
let airportCoordinates_From = [];
let airportCoordinates_To = [];

export function setAirportCoordinates(coordinates) {
    airportCoordinates = coordinates;
}

export function setFromAirportCoordinates(fromCoordinates) {
    airportCoordinates_From = [fromCoordinates];
}

export function setToAirportCoordinates(toCoordinates) {
    airportCoordinates_To = [toCoordinates];
}

export function startRandomFlightPaths(earth, EARTH_RADIUS, BORDER_OFFSET) {
    if (flightInterval) {
        clearInterval(flightInterval);
    }
    
    if (airportCoordinates.length < 2) {
        console.warn('Not enough airports to create flight paths.');
        return;
    }
    clearAllFlights(earth);
    setInterval(() => {
        const startIndex = Math.floor(Math.random() * airportCoordinates.length);
        let endIndex;
        do {
            endIndex = Math.floor(Math.random() * airportCoordinates.length);
        } while (startIndex === endIndex);

        const start = airportCoordinates[startIndex];
        const end = airportCoordinates[endIndex];

        createFlightPath(start.lat, start.lon, end.lat, end.lon, earth, EARTH_RADIUS, BORDER_OFFSET);
    }, 4000);
}

let flightInterval = null;

export function startFlightsFromAirport(earth, EARTH_RADIUS, BORDER_OFFSET) {
    if (airportCoordinates_From.length === 0 || airportCoordinates.length < 2) {
        console.warn('Not enough airports to create flight paths from the specified airport.');
        return;
    }

    const from = airportCoordinates_From[0];
    if (flightInterval) {
        clearInterval(flightInterval);
    }
    flightInterval = setInterval(() => {
        let endIndex;
        do {
            endIndex = Math.floor(Math.random() * airportCoordinates.length);
        } while (
            airportCoordinates[endIndex].lat === from.lat &&
            airportCoordinates[endIndex].lon === from.lon
        );

        const end = airportCoordinates[endIndex];
        createFlightPath(from.lat, from.lon, end.lat, end.lon, earth, EARTH_RADIUS, BORDER_OFFSET);
    }, 500);
}

export function startFlightsToAirport(earth, EARTH_RADIUS, BORDER_OFFSET) {
    if (airportCoordinates_To.length === 0 || airportCoordinates.length < 2) {
        console.warn('Not enough airports to create flight paths to the specified airport.');
        return;
    }

    const to = airportCoordinates_To[0];
    if (flightInterval) {
        clearInterval(flightInterval);
    }
    flightInterval = setInterval(() => {
        let startIndex;
        do {
            startIndex = Math.floor(Math.random() * airportCoordinates.length);
        } while (
            airportCoordinates[startIndex].lat === to.lat &&
            airportCoordinates[startIndex].lon === to.lon
        );

        const start = airportCoordinates[startIndex];
        createFlightPath(start.lat, start.lon, to.lat, to.lon, earth, EARTH_RADIUS, BORDER_OFFSET);
    }, 500);
}

export function startFlightsFromToAirport(earth, EARTH_RADIUS, BORDER_OFFSET) {
    if (airportCoordinates_From.length === 0 || airportCoordinates_To.length === 0) {
        console.warn('Not enough data to create flight paths between the specified airports.');
        return;
    }

    const from = airportCoordinates_From[0];
    const to = airportCoordinates_To[0];
    if (flightInterval) {
        clearInterval(flightInterval);
    }

    flightInterval = setInterval(() => {
        createFlightPath(from.lat, from.lon, to.lat, to.lon, earth, EARTH_RADIUS, BORDER_OFFSET);
    }, 1200);
}

export function clearAllFlights(earth) {
    activeFlights.forEach(flight => {
        earth.remove(flight);
    });
    activeFlights = [];
}

