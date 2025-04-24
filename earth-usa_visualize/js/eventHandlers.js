export let isDragging = false;
export let previousMousePosition = { x: 0, y: 0 };
export let targetRotation = { x: 0, y: 0 };

let targetZoom = 2;
let currentZoom = 2000;
let targetY = 0;
let currentY = 0;

export let isMouseOverPanel = false;

// General throttle function to optimize mouse move performance
function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function (...args) {
        const context = this;
        if (!lastRan) {
            func.apply(context, args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if (Date.now() - lastRan >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
}

export function initEventListeners(camera, renderer) {
    window.addEventListener('resize', () => onWindowResize(camera, renderer));
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('mousemove', throttle(onMouseMove, 50));
    document.addEventListener('mouseup', onMouseUp);
    document.addEventListener('wheel', throttle((e) => onMouseWheel(e, camera), 50));
    document.addEventListener('gesturestart', onGestureStart);
    document.addEventListener('gesturechange', throttle(onGestureChange, 50));
    document.addEventListener('touchstart', onTouchStart);
    document.addEventListener('touchmove', throttle(onTouchMove, 50));
    document.addEventListener('touchend', onTouchEnd);

    document.addEventListener('mouseover', (event) => {
        if (event.target.closest('.input-panel, .display-panel')) {
            isMouseOverPanel = true;
        }
    });

    document.addEventListener('mouseout', (event) => {
        if (event.target.closest('.input-panel, .display-panel')) {
            isMouseOverPanel = false;
        }
    });
}

function onWindowResize(camera, renderer) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onMouseDown(e) {
    if (isMouseOverPanel) return;
    isDragging = true;
    previousMousePosition = { x: e.clientX, y: e.clientY };
}

function onMouseMove(e) {
    if (isMouseOverPanel || !isDragging) return;
    const deltaMove = { x: e.clientX - previousMousePosition.x, y: e.clientY - previousMousePosition.y };
    const sensitivity = 0.002;
    targetRotation.y += deltaMove.x * sensitivity;
    targetRotation.x += deltaMove.y * sensitivity;
    previousMousePosition = { x: e.clientX, y: e.clientY };
}

function onMouseUp() {
    if (isMouseOverPanel) return;
    isDragging = false;
}

function onMouseWheel(event, camera) {
    if (isMouseOverPanel) return;

    const zoomSpeed = 0.0005;
    const yShiftSpeed = 0.00011;

    targetZoom += event.deltaY * zoomSpeed;
    targetZoom = Math.max(1.8, Math.min(4, targetZoom));

    const yShift = event.deltaY * yShiftSpeed;
    targetY -= yShift;
    targetY = Math.max(-0.48, Math.min(0, targetY));
}

function onGestureStart(event) {
    event.preventDefault();
}

function onGestureChange(event) {
    event.preventDefault();
    if (isMouseOverPanel) return;

    const zoomSpeed = 0.05;
    if (event.scale > 1) {
        targetZoom -= (event.scale - 1) * zoomSpeed;
    } else {
        targetZoom += (1 - event.scale) * zoomSpeed;
    }
    targetZoom = Math.max(1.8, Math.min(4, targetZoom));
}

let isTouching = false;
let previousTouchPositions = [];
let initialDistance = null;

function onTouchStart(event) {
    if (isMouseOverPanel) return;

    if (event.touches.length === 1) {
        isTouching = true;
        previousTouchPositions = [{ x: event.touches[0].clientX, y: event.touches[0].clientY }];
    } else if (event.touches.length === 2) {
        isTouching = false;
        initialDistance = getDistance(event.touches[0], event.touches[1]);
    }
}

function onTouchMove(event) {
    if (isMouseOverPanel) return;

    if (event.touches.length === 1 && isTouching) {
        const currentTouch = { x: event.touches[0].clientX, y: event.touches[0].clientY };
        const deltaMove = {
            x: currentTouch.x - previousTouchPositions[0].x,
            y: currentTouch.y - previousTouchPositions[0].y,
        };
        const sensitivity = 0.002;
        targetRotation.y += deltaMove.x * sensitivity;
        targetRotation.x += deltaMove.y * sensitivity;
        previousTouchPositions = [currentTouch];
    } else if (event.touches.length === 2) {
        const currentDistance = getDistance(event.touches[0], event.touches[1]);
        const zoomSpeed = 0.003;
        if (initialDistance) {
            targetZoom += (initialDistance - currentDistance) * zoomSpeed;
            targetZoom = Math.max(1.8, Math.min(4, targetZoom));
        }
        initialDistance = currentDistance;
    }
}

function onTouchEnd(event) {
    if (event.touches.length === 0) {
        isTouching = false;
        initialDistance = null;
    }
}

function getDistance(touch1, touch2) {
    const dx = touch2.clientX - touch1.clientX;
    const dy = touch2.clientY - touch1.clientY;
    return Math.sqrt(dx * dx + dy * dy);
}

export function updateZoom(camera) {
    if (isMouseOverPanel) return;

    const easingFactor = 0.1;
    currentZoom += (targetZoom - currentZoom) * easingFactor;
    currentY += (targetY - currentY) * easingFactor;

    camera.position.z = currentZoom;
    camera.position.y = currentY;
}
