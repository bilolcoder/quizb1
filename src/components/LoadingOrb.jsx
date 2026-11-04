import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export default function LoadingOrb({ onComplete }) {
  const mountRef = useRef(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // 5 seconds total duration
    const DURATION = 5000;
    const startTime = performance.now();

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      1,
      1000
    );
    camera.position.z = 240;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Particle count: 1200 particles for dense, glowing orb
    const count = 1200;
    const positions = new Float32Array(count * 3);
    const startPositions = new Float32Array(count * 3);
    const orbPositions = new Float32Array(count * 3);
    const endPositions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const greenColor = new THREE.Color('#9CD296');
    const lightGreen = new THREE.Color('#C4E8BF');
    const whiteColor = new THREE.Color('#FFFFFF');

    // Generate random scattered start, spherical orb target, and dispersed end positions
    const orbRadius = 45;
    for (let i = 0; i < count; i++) {
      // 1. Initial random scattered positions across screen
      startPositions[i * 3] = (Math.random() - 0.5) * 500;
      startPositions[i * 3 + 1] = (Math.random() - 0.5) * 450;
      startPositions[i * 3 + 2] = (Math.random() - 0.5) * 300;

      // Current start position
      positions[i * 3] = startPositions[i * 3];
      positions[i * 3 + 1] = startPositions[i * 3 + 1];
      positions[i * 3 + 2] = startPositions[i * 3 + 2];

      // 2. Spherical Particle Orb target positions (Fibonacci sphere distribution)
      const phi = Math.acos(1 - 2 * (i + 0.5) / count);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      const r = orbRadius * (0.85 + Math.random() * 0.3);

      orbPositions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      orbPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      orbPositions[i * 3 + 2] = r * Math.cos(phi);

      // 3. Final dispersed positions (radiating outwards at completion)
      const burstFactor = 3.5 + Math.random() * 2;
      endPositions[i * 3] = orbPositions[i * 3] * burstFactor;
      endPositions[i * 3 + 1] = orbPositions[i * 3 + 1] * burstFactor;
      endPositions[i * 3 + 2] = orbPositions[i * 3 + 2] * burstFactor;

      // Color palette: glowing emerald greens and sparkling whites
      const rand = Math.random();
      const col = rand > 0.6 ? whiteColor : rand > 0.25 ? greenColor : lightGreen;
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle texture
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
    grad.addColorStop(0.3, 'rgba(156, 210, 150, 0.9)');
    grad.addColorStop(0.7, 'rgba(156, 210, 150, 0.25)');
    grad.addColorStop(1, 'rgba(156, 210, 150, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 64, 64);
    const texture = new THREE.CanvasTexture(canvas);

    const material = new THREE.PointsMaterial({
      size: 7,
      map: texture,
      transparent: true,
      opacity: 0.9,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const orbMesh = new THREE.Points(geometry, material);
    scene.add(orbMesh);

    // Inner glowing sphere core
    const coreGeo = new THREE.SphereGeometry(22, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color('#9CD296'),
      transparent: true,
      opacity: 0.22,
      blending: THREE.AdditiveBlending
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);

    // Easing helper
    const easeInOutCubic = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    let animId;

    const animate = (now) => {
      const elapsed = Math.min(now - startTime, DURATION);
      const linearProgress = elapsed / DURATION;
      setProgress(Math.floor(linearProgress * 100));

      const posArray = geometry.attributes.position.array;

      // Phase 1: 0.0s - 1.8s -> Particles gather from scatter into sphere orb
      // Phase 2: 1.8s - 4.2s -> Orb revolves with internal soft green pulse
      // Phase 3: 4.2s - 5.0s -> Orb smoothly disperses outwards
      if (linearProgress < 0.36) {
        // Gathering phase
        const t = easeInOutCubic(linearProgress / 0.36);
        for (let i = 0; i < count; i++) {
          posArray[i * 3] = startPositions[i * 3] + (orbPositions[i * 3] - startPositions[i * 3]) * t;
          posArray[i * 3 + 1] = startPositions[i * 3 + 1] + (orbPositions[i * 3 + 1] - startPositions[i * 3 + 1]) * t;
          posArray[i * 3 + 2] = startPositions[i * 3 + 2] + (orbPositions[i * 3 + 2] - startPositions[i * 3 + 2]) * t;
        }
        coreMat.opacity = t * 0.25;
      } else if (linearProgress < 0.84) {
        // Pure rotating glowing orb phase
        const pulse = 1 + Math.sin((elapsed - 1800) * 0.006) * 0.08;
        for (let i = 0; i < count; i++) {
          posArray[i * 3] = orbPositions[i * 3] * pulse;
          posArray[i * 3 + 1] = orbPositions[i * 3 + 1] * pulse;
          posArray[i * 3 + 2] = orbPositions[i * 3 + 2] * pulse;
        }
        coreMesh.scale.set(pulse, pulse, pulse);
        coreMat.opacity = 0.2 + Math.sin((elapsed - 1800) * 0.008) * 0.1;
      } else {
        // Disperse phase (4.2s to 5.0s)
        const t = easeInOutCubic((linearProgress - 0.84) / 0.16);
        for (let i = 0; i < count; i++) {
          posArray[i * 3] = orbPositions[i * 3] + (endPositions[i * 3] - orbPositions[i * 3]) * t;
          posArray[i * 3 + 1] = orbPositions[i * 3 + 1] + (endPositions[i * 3 + 1] - orbPositions[i * 3 + 1]) * t;
          posArray[i * 3 + 2] = orbPositions[i * 3 + 2] + (endPositions[i * 3 + 2] - orbPositions[i * 3 + 2]) * t;
        }
        material.opacity = 0.9 * (1 - t * 0.7);
        coreMat.opacity = 0.25 * (1 - t);
      }

      geometry.attributes.position.needsUpdate = true;

      // Slow rotating orb
      orbMesh.rotation.y += 0.012;
      orbMesh.rotation.x += 0.006;
      coreMesh.rotation.y -= 0.008;

      renderer.render(scene, camera);

      if (elapsed < DURATION) {
        animId = requestAnimationFrame(animate);
      } else {
        if (onComplete) onComplete();
      }
    };

    animId = requestAnimationFrame(animate);

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      texture.dispose();
      renderer.dispose();
    };
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#F5F9F4]/75 backdrop-blur-xl">
      {/* Three.js Canvas mount */}
      <div ref={mountRef} className="absolute inset-0 pointer-events-none" />

      {/* Floating Status Card */}
      <div className="relative z-10 flex flex-col items-center text-center max-w-sm px-6 py-6 glass-card rounded-3xl mt-48 pointer-events-auto">
        <p className="text-sm font-semibold tracking-wide text-[#263528] mb-3">
          Bilimingiz sinovga tayyorlanmoqda...
        </p>

        {/* Progress Bar */}
        <div className="w-64 h-2 bg-white/70 rounded-full overflow-hidden border border-[#9CD296]/30 shadow-inner p-0.5">
          <div
            className="h-full bg-gradient-to-r from-[#9CD296] to-[#7EBF77] rounded-full transition-all duration-75"
            style={{ width: `${progress}%` }}
          />
        </div>

        <span className="text-xs font-mono font-medium text-[#263528]/70 mt-2">
          {progress}%
        </span>
      </div>
    </div>
  );
}

