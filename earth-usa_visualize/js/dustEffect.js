export function createDust(earth) {
    const particleCount = 5000; // Number of particles
    const particleGeometry = new THREE.BufferGeometry();
    const positions = [];
    const velocities = []; // Store velocity for each particle

    for (let i = 0; i < particleCount; i++) {
        const x = (Math.random() - 0.5) * 10;
        const y = (Math.random() - 0.5) * 10;
        const z = (Math.random() - 0.5) * 10;
        positions.push(x, y, z);

        const vx = (Math.random() - 0.5) * 0.0001;
        const vy = (Math.random() - 0.5) * 0.0001;
        const vz = (Math.random() - 0.5) * 0.0001;
        velocities.push(vx, vy, vz);
    }

    particleGeometry.setAttribute(
        'position',
        new THREE.Float32BufferAttribute(positions, 3)
    );

    const textureLoader = new THREE.TextureLoader();
    const particleTexture = textureLoader.load('assets/circle.png'); // Ensure the path is correct

    const particleMaterial = new THREE.PointsMaterial({
        map: particleTexture,      // Use circular texture
        color: 0xa2efe1,           // Particle color
        size: 0.01,                // Particle size
        transparent: true,         // Enable transparency
        opacity: 0.8,              // Particle opacity
        // blending: THREE.AdditiveBlending, // Additive blending effect
        depthWrite: false          // Disable depth writing to avoid occlusion
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    particles.userData.velocities = velocities; // Store velocities in userData

    earth.add(particles);

    return particles; // Return particle system object
}

export function updateDust(particles) {
    const positions = particles.geometry.attributes.position.array;
    const velocities = particles.userData.velocities;
    
    const gravityFactor = 0.0000;     // Extremely weak gravitational field
    const spaceResistance = 0.9999;  // Almost no resistance in space
    const solarWindStrength = 0.0000002; // Solar wind strength
    const solarWindDirection = { x: 0.5, y: 0.2, z: -0.1 }; // Solar wind direction

    for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const y = positions[i + 1];
        const z = positions[i + 2];
        const distanceSquared = x * x + y * y + z * z;
        const distance = Math.sqrt(distanceSquared);
        
        if (distance > 0.1) {
            const gravitationalForce = gravityFactor / distanceSquared;
            velocities[i] -= (x / distance) * gravitationalForce;
            velocities[i + 1] -= (y / distance) * gravitationalForce;
            velocities[i + 2] -= (z / distance) * gravitationalForce;
        }
        
        velocities[i] *= spaceResistance;
        velocities[i + 1] *= spaceResistance;
        velocities[i + 2] *= spaceResistance;

        velocities[i] += solarWindDirection.x * solarWindStrength;
        velocities[i + 1] += solarWindDirection.y * solarWindStrength;
        velocities[i + 2] += solarWindDirection.z * solarWindStrength;

        const quantumTurbulence = 0.00005; // Random disturbance in interstellar medium
        velocities[i] += (Math.random() - 0.5) * quantumTurbulence;
        velocities[i + 1] += (Math.random() - 0.5) * quantumTurbulence;
        velocities[i + 2] += (Math.random() - 0.5) * quantumTurbulence;

        positions[i] += velocities[i];
        positions[i + 1] += velocities[i + 1];
        positions[i + 2] += velocities[i + 2];

        const boundary = 5; // Expanded boundary range
        if (Math.abs(positions[i]) > boundary || 
            Math.abs(positions[i + 1]) > boundary || 
            Math.abs(positions[i + 2]) > boundary) {
            
            const phi = Math.random() * Math.PI * 2; // Random angle
            const theta = Math.acos(2 * Math.random() - 1); // Uniform distribution on sphere
            const radius = boundary * 0.9;
            
            positions[i] = radius * Math.sin(theta) * Math.cos(phi);
            positions[i + 1] = radius * Math.sin(theta) * Math.sin(phi);
            positions[i + 2] = radius * Math.cos(theta);
            
            const initialSpeed = 0.001;
            velocities[i] = -positions[i] / radius * initialSpeed * Math.random();
            velocities[i + 1] = -positions[i + 1] / radius * initialSpeed * Math.random();
            velocities[i + 2] = -positions[i + 2] / radius * initialSpeed * Math.random();
        }
    }

    particles.geometry.attributes.position.needsUpdate = true;
}