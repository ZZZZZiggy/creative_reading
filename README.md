# Cognitive-Aware Reading System Development Plan

This plan adopts a decoupled frontend-backend architecture.

**Core Philosophy:** Frontend focuses on Visual Computing & Interactive Rendering; Backend focuses on Unstructured Text Cleaning & Semantic Structuring.

## 1. The Core Contract

The single source of truth for frontend-backend collaboration is the data structure. The backend produces this metadata, and the frontend visualizes it.

**API:** `GET /api/v1/documents/{doc_id}/content`

```json
{
  "doc_id": "uuid_123",
  "title": "Understanding Quantum Entanglement",
  "meta": {
    "difficulty": "Hard",
    "domain": "Physics",
    "language": "en-US"
  },
  "blocks": [
    {
      "id": "blk_01",
      "type": "paragraph",
      "content": "Quantum entanglement is a physical phenomenon that occurs...",
      // Core: All metadata required for UI rendering
      "annotations": {
        // [Skim Mode] Core: Range of the topic sentence
        "topic_sentence_range": [0, 42],
        // [Skim Mode] Advanced: Syntax structure highlighting (S-V-O)
        "svo_structure": [[0, 18], [19, 21], [22, 42]],
        // [Intensive Mode] Bilingual anchors & jargon explanation
        "bilingual_anchors": [
          {
            "term": "entanglement",
            "range": [8, 20],
            "translation": "纠缠",
            "nuance_note": "Core concept of the EPR paradox; Einstein called it 'spooky action at a distance'.",
            "trigger_threshold_ms": 800 // Optional: Gaze duration required to trigger this anchor
          }
        ]
      }
    }
  ]
}
```

## 2. Frontend Development Manual

**Goal:** Build an immersive interactive canvas with zero latency and no layout shifts, supporting Pupil Labs hardware integration.

### 2.1 Recommended Engineering Structure

```
src/
├── components/
│   ├── Reader/
│   │   ├── Canvas.tsx       # Main canvas, handles layout
│   │   ├── Paragraph.tsx    # Renders single paragraph, handles Opacity logic
│   │   ├── AnchorOverlay.tsx # Bilingual anchor overlay/sidebar (Marginalia)
│   │   └── CalibrationTags.tsx # Renders AprilTags at the 4 screen corners
├── hooks/
│   ├── useEyeTracker.ts     # Unified wrapper for WebGazer and Pupil Labs WebSocket
│   ├── useGazeFilter.ts     # Kalman Filter logic
│   └── useHitTest.ts        # Algorithm mapping Coordinates -> DOM IDs
├── stores/
│   └── useReadingState.ts   # Zustand store (Scanning/Reading/Fixating)
```

### 2.2 Frontend Detailed Roadmap

#### Phase 0: Core Verification & Hardware Integration (Proof of Concept)

**Task F-0.1 (WebGazer PoC):**
- Integrate webgazer.js.
- Implement a simple 9-point calibration flow UI.

**Task F-0.2 (Pupil Labs Surface Integration):**
- **Surface Markers:** Create a CalibrationTags component to render AprilTag 36h11 family tags (IDs 0-3) at the four screen corners (fixed position).
- **WebSocket:** Use react-use-websocket to connect to the Pupil Invisible/Neon Companion App (`ws://<ip>:<port>`).
- **Data Subscription:** Subscribe to the surface topic to receive normalized coordinates (norm_x, norm_y).

#### Phase 2: Reader UI Development (The Reader UI)

**Task F-2.1 (Layout Engine):**
- **Typography Specs:** Use Georgia or Merriweather (Serif) for body text and Inter (Sans) for UI. Line height leading-loose (2.0).
- **ID Binding:** When rendering, `<p id={block.id}>` is mandatory.

**Task F-2.2 (Visual Filters):**
- **Skim Mode Implementation:**
  ```css
  .skim-mode .non-topic {
    opacity: 0.3;
    filter: blur(0.5px);
    transition: all 0.4s ease;
  }
  .skim-mode .topic-sentence {
    opacity: 1;
    font-weight: 600;
  }
  ```

**Task F-2.3 (Anchor UI):**
- **Ghost Underline:** Use `border-bottom: 2px solid rgba(var(--primary-color), 0.1)`.
- **Marginalia (Sidebar):** Use `position: absolute; right: -200px` to render translations outside the article container. Use CSS transform to reveal them to avoid Reflow.

#### Phase 3: Eye-Tracking Integration & State Machine (Integration)

**Task F-3.1 (Hit Test Algorithm):**
- **Pain Point:** `document.elementFromPoint(x, y)` has poor performance.
- **Optimization:** After the article loads, use `getBoundingClientRect` to cache the physical coordinate ranges of all paragraphs into an RBush index or a simple array. Update the cache only on Scroll events.

**Task F-3.2 (Intent Classifier State Machine):**
- **Input:** Filtered (x, y) stream.
- **Logic Pseudocode:**
  ```javascript
  if (velocity > 500px/s) setMode('SCANNING'); // Fast eye movement -> Skim Mode
  else if (velocity < 50px/s && sameElement) {
     fixationTimer += delta;
     if (fixationTimer > 800ms) setMode('FIXATING'); // Staring -> Expand Anchor
  }
  else setMode('READING'); // Linear reading -> Keep highlight
  ```

**Task F-3.3 (Smoothing):**
- Implement a 1D Kalman Filter to process X and Y axes independently. Recommended: Q (Process Noise) = 1e-5, R (Measurement Noise) = 0.01.

## 3. Backend Development Manual

**Goal:** Establish an automated "Refining Pipeline" to transform unstructured documents into high-value structured data.

### 3.1 Backend Tech Stack

- **Framework:** Python FastAPI
- **Pipeline:**
  - PDF to Markdown: Marker (PyTorch-based)
  - NLP: LangChain + GPT-4o-mini (for semantic extraction)
- **Database:** PostgreSQL (pgvector) + Redis

### 3.2 Detailed API Definition

| Method | Path | Description | Body / Params |
|--------|------|-------------|---------------|
| POST | `/documents/upload` | Upload PDF | `file: UploadFile, native_language: str` |
| GET | `/documents/{id}/status` | Query processing status | Returns: `{"stage": "marker_processing", "percent": 40}` |
| GET | `/documents/{id}/content` | Get JSON for rendering | Returns: `DocumentSchema` |
| POST | `/analytics/gaze` | Submit heatmap data | Body: `{"doc_id": "...", "fixations": [{"blk_id": "p1", "duration": 400}]}` |

### 3.3 Backend Detailed Roadmap

#### Phase 1: Pipeline Construction (The Pipeline)

**Task B-1.1 (Marker Integration):**
- Configure Marker parameters: `--batch_multiplier 2` (optimized for GPU), `--langs English`.
- **Output Cleaning:** Remove image links and tables generated by Marker from the Markdown (Ignore complex tables for MVP).

**Task B-1.2 (Prompt Engineering - Core Task):**
- **System Prompt:**
  - You are a cognitive reading assistant.
  - Identify the single most important "Topic Sentence" in the paragraph.
  - Identify 1-2 technical terms that are abstract. Provide a "Bilingual Anchor": a translation into `{user_language}` that captures the cultural nuance or core concept, not just a literal dictionary definition.
- **Return JSON:** `{"topic_start": int, "topic_end": int, "anchors": [{"term": "...", "translation": "..."}]}`

**Task B-1.3 (Structure Parsing):**
- Merge the plain text output from Marker with the JSON indices from the LLM. Note: LLMs may "hallucinate" character indices. It is recommended to have the LLM return the quoted text, and let the backend use Fuzzy Match to determine the exact index position.

#### Phase 4: Analytics & Generation (Analytics)

**Task B-4.1 (Review Generator):**
- **Logic:** Query paragraphs in the database where `duration > avg_duration * 2`.
- **Prompt:** "User struggled with these specific concepts: [List]. Generate a 3-bullet summary explaining these concepts in simple analogies."
