export let earth;
export let earthGlow;

export function initEarth(scene, EARTH_RADIUS, BORDER_OFFSET) {
    const geometry = new THREE.SphereGeometry(EARTH_RADIUS, 128, 128);

    const material = new THREE.ShaderMaterial({
        uniforms: {
            color: { value: new THREE.Color(0x2596be) },
            opacityTop: { value: 0.2 },
            opacityBottom: { value: 0 },
            glowColor: { value: new THREE.Color(0x00a3ff) },
            glowPower: { value: 3.0 }
        },
        vertexShader: `
            varying float vHeight;
            varying vec3 vNormal;
            varying vec3 vViewDir;

            void main() {
                vHeight = position.y;
                
                vNormal = normalize(normalMatrix * normal);
                vec4 worldPosition = modelMatrix * vec4(position, 1.0);
                vViewDir = normalize(cameraPosition - worldPosition.xyz);
                
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 color;
            uniform float opacityTop;
            uniform float opacityBottom;
            uniform vec3 glowColor;
            uniform float glowPower;
            varying float vHeight;
            varying vec3 vNormal;
            varying vec3 vViewDir;

            void main() {
                float opacity = mix(opacityBottom, opacityTop, (vHeight + 1.0) / 2.0);
                
                float rim = 1.0 - dot(vNormal, vViewDir);
                rim = smoothstep(0.4, 1.0, rim);
                rim = pow(rim, glowPower);
                
                vec3 finalColor = mix(color, glowColor, rim);
                
                gl_FragColor = vec4(finalColor, opacity);
            }
        `,
        transparent: true
    });

    earth = new THREE.Mesh(geometry, material);

    earth.position.set(0, -0.5, 0.7);
    earth.rotation.y = Math.PI / 4;
    earth.rotation.x = Math.PI / 4;
    scene.add(earth);
}

export function latLongToVector3(lat, lon, radius) {
    const phi = THREE.MathUtils.degToRad(90 - lat);
    const theta = THREE.MathUtils.degToRad(lon);
    
    const x = radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.cos(phi);
    const z = -radius * Math.sin(phi) * Math.sin(theta);
    
    return new THREE.Vector3(x, y, z);
}


