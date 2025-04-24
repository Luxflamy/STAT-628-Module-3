import { latLongToVector3 } from './earthModel.js';

export function loadGeoJSON(url, lineColor, lineWidth, earth, EARTH_RADIUS, BORDER_OFFSET) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            data.features.forEach(feature => {
                if (feature.geometry.type === 'Polygon') {
                    processPolygon(feature.geometry.coordinates, lineColor, lineWidth, earth, EARTH_RADIUS, BORDER_OFFSET);
                } else if (feature.geometry.type === 'MultiPolygon') {
                    feature.geometry.coordinates.forEach(polygon => {
                        processPolygon(polygon, lineColor, lineWidth, earth, EARTH_RADIUS, BORDER_OFFSET);
                    });
                }
            });
        });
}

export const iataToCoordinates = {}; // Global object to store IATA to latitude/longitude mapping
export function loadAirports(url, earth, EARTH_RADIUS, BORDER_OFFSET) {
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            const airportCoordinates = [];
            data.features.forEach(feature => {
                if (feature.geometry.type === 'Point') {
                    const [longitude, latitude] = feature.geometry.coordinates;
                    const traffic = feature.properties.TOT_ENP || 0; // Get airport traffic
                    const iata = feature.properties.IATA || ''; // Get IATA code
                    if (iata) {
                        iataToCoordinates[iata] = { lat: latitude, lon: longitude }; // Store mapping
                    }
                    addAirportMarker(latitude, longitude, earth, EARTH_RADIUS, BORDER_OFFSET, traffic);
                    airportCoordinates.push({ lat: latitude, lon: longitude });
                }
            });
            return airportCoordinates; // Return array of airport coordinates
        });
}

function processPolygon(coordinates, lineColor, lineWidth, earth, EARTH_RADIUS, BORDER_OFFSET) {
    const lineMaterial = new THREE.LineBasicMaterial({
        color: lineColor,
        linewidth: lineWidth,
        opacity: 0.9,
        depthWrite: false
    });
    const points = coordinates[0].map(coord => {
        const [longitude, latitude] = coord;
        return latLongToVector3(latitude, longitude, EARTH_RADIUS + BORDER_OFFSET);
    });
    if (points.length > 0) points.push(points[0].clone());
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, lineMaterial);
    earth.add(line);

    addDotPattern(coordinates, earth, EARTH_RADIUS + BORDER_OFFSET);
}

function addDotPattern(coordinates, earth, radius) {
    const dotMaterial = new THREE.PointsMaterial({
        color: 0x2596be,
        size: 0.005,
        transparent: true,
        opacity: 0.15,
    });

    const dots = [];
    const step = 0.7;

    for (let lat = -90; lat <= 90; lat += step) {
        for (let lon = -180; lon <= 180; lon += step) {
            if (isPointInsidePolygon(lat, lon, coordinates)) {
                const position = latLongToVector3(lat, lon, radius);
                dots.push(position);
            }
        }
    }

    const dotGeometry = new THREE.BufferGeometry().setFromPoints(dots);
    const dotMesh = new THREE.Points(dotGeometry, dotMaterial);
    earth.add(dotMesh);
}

/**
 * Check if a point is inside a polygon
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @param {Array} polygon - Polygon coordinates array
 * @returns {boolean} Whether the point is inside the polygon
 */
function isPointInsidePolygon(lat, lon, polygon) {
    let inside = false;
    const x = lon, y = lat;
    const vs = polygon[0];

    for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        const xi = vs[i][0], yi = vs[i][1];
        const xj = vs[j][0], yj = vs[j][1];

        const intersect = ((yi > y) !== (yj > y)) &&
                          (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }

    return inside;
}

const airportPositions = []; // Store all airport 3D positions

function addAirportMarker(lat, lon, earth, EARTH_RADIUS, BORDER_OFFSET, traffic) {
    const baseRadius = 0.0004;
    const scaleFactor = 0.001;

    const dynamicRadius = baseRadius + Math.log10(traffic + 1) * scaleFactor;

    console.log(`Airport at (${lat}, ${lon}) with traffic ${traffic} has radius ${dynamicRadius.toFixed(6)}`);

    const circleOpacity = 0.2;
    const circleColor = 0xff6361;

    const smallGeometry = new THREE.CircleGeometry(dynamicRadius * 0.5, 32);
    const smallMaterial = new THREE.MeshBasicMaterial({
        color: circleColor,
        transparent: true,
        opacity: circleOpacity
    });
    const smallCircle = new THREE.Mesh(smallGeometry, smallMaterial);

    const mediumGeometry = new THREE.CircleGeometry(dynamicRadius, 32);
    const mediumMaterial = new THREE.MeshBasicMaterial({
        color: circleColor,
        transparent: true,
        opacity: circleOpacity
    });
    const mediumCircle = new THREE.Mesh(mediumGeometry, mediumMaterial);

    const largeGeometry = new THREE.CircleGeometry(dynamicRadius * 1.5, 32);
    const largeMaterial = new THREE.MeshBasicMaterial({
        color: circleColor,
        transparent: true,
        opacity: circleOpacity
    });
    const largeCircle = new THREE.Mesh(largeGeometry, largeMaterial);

    let position = latLongToVector3(lat, lon, EARTH_RADIUS + BORDER_OFFSET + 0.001);
    position = resolveOverlap(position);

    const normal = position.clone().normalize();
    smallCircle.position.copy(position.clone().add(normal.clone().multiplyScalar(0.0003)));
    mediumCircle.position.copy(position.clone().add(normal.clone().multiplyScalar(0.0002)));
    largeCircle.position.copy(position.clone().add(normal.clone().multiplyScalar(0.0001)));

    smallCircle.lookAt(normal.add(smallCircle.position));
    mediumCircle.lookAt(normal.add(mediumCircle.position));
    largeCircle.lookAt(normal.add(largeCircle.position));

    earth.add(smallCircle);
    earth.add(mediumCircle);
    earth.add(largeCircle);

    addAirportLabelAndLine(lat, lon, earth, EARTH_RADIUS, BORDER_OFFSET, traffic, circleColor);

    airportPositions.push(position);
}

function addAirportLabelAndLine(lat, lon, earth, EARTH_RADIUS, BORDER_OFFSET, traffic, color) {
    const heightFactor = 0.00008;
    const height = Math.sqrt(traffic) * heightFactor;

    const labelGeometry = new THREE.SphereGeometry(0.0005, 16, 16);
    const labelMaterial = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.8
    });
    const label = new THREE.Mesh(labelGeometry, labelMaterial);

    const labelPosition = latLongToVector3(lat, lon, EARTH_RADIUS + BORDER_OFFSET + 0.00001 + height);
    label.position.copy(labelPosition);

    const start = latLongToVector3(lat, lon, EARTH_RADIUS + BORDER_OFFSET + 0.00001);
    const end = labelPosition.clone();
    const lineGeometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const lineMaterial = new THREE.LineBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.8
    });
    const line = new THREE.Line(lineGeometry, lineMaterial);

    earth.add(label);
    earth.add(line);
}

/**
 * Detect and resolve airport marker overlap
 * @param {THREE.Vector3} position - Current airport 3D position
 * @returns {THREE.Vector3} Adjusted 3D position
 */
function resolveOverlap(position) {
    const minDistance = 0.01;
    for (const existingPosition of airportPositions) {
        if (position.distanceTo(existingPosition) < minDistance) {
            const offset = position.clone().sub(existingPosition).normalize().multiplyScalar(minDistance);
            position.add(offset);
        }
    }
    return position;
}
