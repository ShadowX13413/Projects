# Interactive Web Lab • Canvas & Web Audio Experiments

A curated collection of zero-dependency, browser-native applications, games, and mathematical visualizers built with vanilla HTML5, Canvas 2D, and procedural Web Audio synthesis. 

Every project is self-contained in a single executable HTML file—no build pipeline, no package managers, and no external assets required.

---

## Technical Stack

* **Language:** Vanilla JavaScript (ES6+), HTML5
* **Rendering Engine:** Canvas 2D API (`requestAnimationFrame` game loops)
* **Audio Engine:** Web Audio API (procedurally synthesized sound effects; zero external `.mp3`/`.wav` assets)
* **Styling & Typography:** Pure CSS, Tailwind CSS (in select visualizers), Google Fonts (`Press Start 2P`)

---

## Project Directory & Architecture

Projects/
├── Mario.html                   # 141 KB  • "Super Plumber Bros" NES-style platformer
├── Galaxy game.html             # 33.0 KB • "Galactic Interceptor" space shooter with boss AI
├── Particles.html               # 15.5 KB • 1,800-entity neural & fluid dynamics sandbox
├── neuralnetworkspreview.html   # 18.5 KB • Interactive forward-pass matrix math visualizer
├── E-commerceWebsite.html       # 5.9 KB  • Product catalog UI with dynamic cart state
├── Htmltable.html               # 2.7 KB  • Semantic data layout demonstration
└── Jarvis/                      # Directory • Experimental / WIP workspace

---

## Application Breakdown

### 1. Super Plumber Bros (`Mario.html`)
* **Type:** 2D Platformer Game
* **Footprint:** ~141 KB
* **Core Mechanics:** Tile-based collision detection, jump kinematics, running momentum, projectile mechanics, and retro procedural audio cues.
* **Controls:**
  * Move: `A` / `D` or `Left` / `Right` Arrows
  * Jump: `W`, `Space`, or `Up` Arrow
  * Run / Shoot: `X` or `Shift`

### 2. Galactic Interceptor (`Galaxy game.html`)
* **Type:** Arcade Space Shooter
* **Footprint:** ~33 KB
* **Core Mechanics:** Dynamic entity pooling, continuous velocity vectors, timed wave spawning, and automated boss encounters every 30 seconds.
* **Controls:**
  * Flight: `W` `A` `S` `D` or Arrow Keys
  * Fire Weapon: `Left Click`

### 3. Neural Particle Sandbox (`Particles.html`)
* **Type:** Kinetic & Fluid Simulation
* **Footprint:** ~15.5 KB
* **Core Mechanics:** $O(N)$ spatial grid partitioning managing 1,800 simultaneous entities at 60 FPS, logarithmic spiral idle states, and switchable Swarm/Chaos/Neural kinetic modes.
* **Controls:**
  * Gravity Well (Attract): `Left Click` (Hold)
  * Repulsion Field: `Right Click` (Hold)
  * Chaos Burst: `Left` + `Right Click` (Hold)
  * Kinetic Shockwave: `Double Click`

### 4. Neural Network 101 (`neuralnetworkspreview.html`)
* **Type:** Educational Machine Learning Visualizer
* **Footprint:** ~18.5 KB
* **Core Mechanics:** Step-by-step graphic representation of node weight calculation, bias offsets, activation functions, and forward-pass propagation.
* **Controls:**
  * Adjust parameters using the input sliders
  * Click **"Run Forward Pass"** to trigger animated signal propagation

### 5. E-Commerce Catalog (`E-commerceWebsite.html`)
* **Type:** Client-Side Application UI
* **Footprint:** ~5.9 KB
* **Core Mechanics:** Lightweight DOM state management, product filtering, dynamic cart calculations, and responsive interface layout.

---

## Quickstart & Execution

Because all projects rely strictly on browser-native APIs, there is no need for `npm install`, compilers, or local web servers.

### 1. Clone the Repository
```bash
git clone [https://github.com/ShadowX13413/Projects.git](https://github.com/ShadowX13413/Projects.git)
cd Projects
```

2. Launch Any Experiment
Open any target file directly in your default browser:

macOS:

```bash
open Mario.html
open "Galaxy game.html"
open Particles.html
```

Linux:

```bash
xdg-open Mario.html
xdg-open "Galaxy game.html"
xdg-open Particles.html
```

Windows:

```PowerShell
start Mario.html
start "Galaxy game.html"
start Particles.html
```
---

Design Principles
Self-Containment: Everything required to run the application (logic, styling, and synthetic sound generation) resides directly in the HTML document.

Zero Runtime Overhead: No virtual DOM, third-party state managers, or bloated bundle sizes.

Direct Hardware Access: Direct manipulation of the Canvas pixel buffer and Web Audio oscillator nodes for predictable 60 FPS execution.







































