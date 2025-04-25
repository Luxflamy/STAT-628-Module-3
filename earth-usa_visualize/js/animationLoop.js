import { updateDust } from './dustEffect.js';
import { updateZoom } from './eventHandlers.js';

let rotationDirection = 1; // 1 for clockwise, -1 for counterclockwise
const ROTATION_LIMIT = Math.PI / 30; // Rotation limit

export function animate(renderer, scene, camera, earth, particles, globalRotation, targetRotation, currentRotation, ROTATION_SPEED) {
    requestAnimationFrame(() => animate(renderer, scene, camera, earth, particles, globalRotation, targetRotation, currentRotation, ROTATION_SPEED));
    
    // Update rotation direction
    globalRotation.y += ROTATION_SPEED * rotationDirection;
    if (globalRotation.y > ROTATION_LIMIT || globalRotation.y < -ROTATION_LIMIT) {
        rotationDirection *= -1; // Reverse direction at boundaries
    }

    const easingFactor = 0.05;
    currentRotation.x += (targetRotation.x - currentRotation.x) * easingFactor;
    currentRotation.y += (targetRotation.y - currentRotation.y) * easingFactor;
    earth.rotation.x = currentRotation.x;
    earth.rotation.y = currentRotation.y + globalRotation.y;

    updateZoom(camera); // Update camera zoom
    updateDust(particles); // Update dust effect
    renderer.render(scene, camera);
}
