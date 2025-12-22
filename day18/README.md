# Day 18: Google Arts & Culture Experiment MVP

**Context:** Google Arts & Culture Laboratory
**Goal:** Create a bi-directional synced audio-visual experience for museum collections.
**Stack:** React + Vite + Tone.js + Framer Motion (Apache 2.0 compliant)
**Data Source:** `matched_items_with_examples.csv` from Day 5 (Processed to `temporal-metadata.json`).

---

## 🎧 The Experience

This experiment demonstrates a "Deep Zoom" gallery that synchronizes with an audio tour.
1.  **Audio -> Visual**: As the narration plays, the relevant artwork is automatically highlighted and zoomed.
2.  **Visual -> Audio**: Clicking an artwork jumps the audio to the specific moment it is discussed.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+

### Setup

1.  **Install Dependencies**
    ```bash
    cd day18
    npm install
    # Note: Downgraded to Vite 5 to support Node 18
    ```

2.  **Add Audio**
    - Place your `museum-tour.mp3` in `day18/public/audio/`.
    - (A placeholder has been created but has no sound).

3.  **Run Development Server**
    ```bash
    npm run dev
    ```
    Access at `http://localhost:5173`.

4.  **Build**
    ```bash
    npm run build
    ```

---

## 🏗 Architecture

### Components
- **`AudioPlayer`**: Manages playback using HTML5 Audio (Tone.js compatible). Emits `timeUpdate` events.
- **`ArtworkGallery`**: Displays artifacts in a grid. Uses `framer-motion` for shared layout animations.
- **`DeepZoom`**: The "Hero" component that expands the active artwork with detailed metadata.
- **`useSyncEngine`**: Custom hook that correlates `audioTime` with `temporal-metadata.json` to find the Active Item.

### Data Pipeline
- Source: `day05/data/processed/matched_items_with_examples.csv`
- Script: `scripts/process-data.js` converts CSV timestamps (HH:MM:SS) to Seconds and generates `src/data/temporal-metadata.json`.

---

## 🎨 Design System (GAC Style)
- **Minimalist**: White space, simple typography (Inter).
- **Motion**: Spring animations for seamless transitions.
- **Focus**: Content-first hierarchy.

---

## Future Improvements
- [ ] Connect to live BigQuery for real-time metadata updates.
- [ ] Implement waveform visualization using Tone.js Analyser.
- [ ] Add multi-language support.
