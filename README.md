# Plant Health Identifier

A Webots-based plant health detection project using color-based logistic regression and automated LED actuation.

## Overview

This repository contains a complete Webots simulation project for detecting plant health status in real time. The system uses camera-based color analysis, a trained logistic regression model, and automated LED control to identify healthy and stressed plants.

## Key Features

- Real-time plant health detection using Webots simulation
- Color-based logistic regression model for plant status classification
- Autonomous LED actuation based on detected plant health
- Modular Webots controllers for data collection, plant identification, and robot behaviors
- Organized documentation and media assets for review and presentation

## Repository Structure

- `src/`
  - `controllers/` — Webots controller scripts and model artifacts
  - `libraries/` — Shared Python modules and helper utilities
  - `plugins/` — Webots plugin components for physics, remote controls, and robot windows
  - `protos/` — Webots proto definitions used by the simulation
- `worlds/` — Webots world assets and project files
- `docs/` — Documentation and simulation media
  - `report/` — Project report and contribution documents
  - `media/` — Screenshots and recorded simulation video
- `LICENSE` — Project license
- `.gitignore` — Recommended ignore rules for source control

## Getting Started

### Prerequisites

- Webots installed on your machine
- Python 3.8+ if running or modifying controller scripts outside Webots

### Running the Simulation

1. Open Webots.
2. Load `worlds/farm_SEP20_my.wbt`.
3. Select the `plant_identifier` controller under `src/controllers/plant_identifier/`.
4. Start simulation to observe real-time plant health detection and LED actuation.

## Main Components

- `src/controllers/plant_identifier/plant_identifier.py` — Primary controller for plant health classification
- `src/controllers/collect_dataset/` — Dataset collection utilities
- `src/controllers/epuck_avoid_collision/`, `epuck_go_forward/`, `four_wheel_avoidance/` — Example robot behavior controllers
- `src/protos/PottedTree.proto` — Custom plant object definition used in the simulation

## Documentation

- `docs/report/` contains the project report and individual contribution files.
- `docs/media/` contains captured screenshots and simulation recordings.

## Notes

Keep this repository structure when extending the simulation or adding new environments, controllers, and documentation.
