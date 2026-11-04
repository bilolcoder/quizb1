import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeBackground() {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      1,
      1000
    );
    camera.position.z = 300;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Particle count: optimize for mobile
    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 80 : 160;
    const maxDistance = isMobile ? 65 : 85;

    // Positions, Velocities, Colors
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const velocities = [];

    // Colors: #9CD296 (0.612, 0.824, 0.588) and White (1, 1, 1)
    const colorGreen = new THREE.Color('#9CD296');
    const colorWhite = new THREE.Color('#FFFFFF');

    const rangeX = isMobile ? 260 : 450;
    const rangeY = isMobile ? 320 : 350;
    const rangeZ = 200;

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * rangeX;
      positions[i * 3 + 1] = (Math.random() - 0.5) * rangeY;
      positions[i * 3 + 2] = (Math.random() - 0.5) * rangeZ;

      // Subtle float velocities
      velocities.push({
        x: (Math.random() - 0.5) * 0.25,
        y: (Math.random() - 0.5) * 0.25,
        z: (Math.random() - 0.5) * 0.15
      });

      // 70% green, 30% white
      const c = Math.random() > 0.3 ? colorGreen : colorWhite;
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }

    // Particle Geometry & Material
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Circle texture for smooth round dots
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.8)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(16, 16, 16, 0, Math.PI * 2);
    ctx.fill();

    const pointTexture = new THREE.CanvasTexture(canvas);

    const particleMaterial = new THREE.PointsMaterial({
      size: isMobile ? 5 : 7,
      map: pointTexture,
      transparent: true,
      opacity: 0.75,
      vertexColors: true,
      depthWrite: false,
      blending: THREE.NormalBlending
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // Connecting Lines
    const linePositions = new Float32Array(particleCount * particleCount * 3);
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));

    const lineMaterial = new THREE.LineBasicMaterial({
      color: new THREE.Color('#9CD296'),
      transparent: true,
      opacity: 0.18,
      depthWrite: false
    });

    const linesMesh = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(linesMesh);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;

    const handleMouseMove = (event) => {
      const halfX = window.innerWidth / 2;
      const halfY = window.innerHeight / 2;
      targetMouseX = (event.clientX - halfX) * 0.04;
      targetMouseY = (event.clientY - halfY) * 0.04;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Resize Handler
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animationFrameId;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Smooth mouse follow
      mouseX += (targetMouseX - mouseX) * 0.03;
      mouseY += (targetMouseY - mouseY) * 0.03;
      camera.position.x = mouseX;
      camera.position.y = -mouseY;
      camera.lookAt(scene.position);

      const pos = particleGeometry.attributes.position.array;

      let lineVertexIndex = 0;

      // Update particle positions
      for (let i = 0; i < particleCount; i++) {
        pos[i * 3] += velocities[i].x;
        pos[i * 3 + 1] += velocities[i].y;
        pos[i * 3 + 2] += velocities[i].z;

        // Bounce back within bounds
        const boundX = rangeX / 2;
        const boundY = rangeY / 2;
        const boundZ = rangeZ / 2;

        if (pos[i * 3] > boundX || pos[i * 3] < -boundX) velocities[i].x *= -1;
        if (pos[i * 3 + 1] > boundY || pos[i * 3 + 1] < -boundY) velocities[i].y *= -1;
        if (pos[i * 3 + 2] > boundZ || pos[i * 3 + 2] < -boundZ) velocities[i].z *= -1;

        // Connect nearby particles with subtle lines
        for (let j = i + 1; j < particleCount; j++) {
          const dx = pos[i * 3] - pos[j * 3];
          const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
          const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

          if (dist < maxDistance) {
            linePositions[lineVertexIndex++] = pos[i * 3];
            linePositions[lineVertexIndex++] = pos[i * 3 + 1];
            linePositions[lineVertexIndex++] = pos[i * 3 + 2];

            linePositions[lineVertexIndex++] = pos[j * 3];
            linePositions[lineVertexIndex++] = pos[j * 3 + 1];
            linePositions[lineVertexIndex++] = pos[j * 3 + 2];
          }
        }
      }

      particleGeometry.attributes.position.needsUpdate = true;
      lineGeometry.setDrawRange(0, lineVertexIndex / 3);
      lineGeometry.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      particleGeometry.dispose();
      particleMaterial.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
      pointTexture.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      style={{ opacity: 0.9 }}
    />
  );
}

