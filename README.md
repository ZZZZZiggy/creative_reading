# Cognitive-Aware Reading System
Version: 2.0
Target Audience: Developers & Designers
Core Philosophy: "Augmented Reading" — Using gaze data to manage cognitive load, not just track it.

---

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## 1. The User Journey (The "Masking" Workflow)

We implement a specific "Ritual" to hide backend processing time (30s-60s). The user must perceive this as a necessary calibration step, not a loading screen.

### Step 1: Entry & Upload

**Interface:** Clean, minimal dropzone.

**Interaction:** Drag & drop PDF.

**Feedback:** Immediate transition to Step 2 upon file release. No "Uploading..." bar; jump straight to the "Ritual."

**API:** `POST /api/upload_pdf`

**Response:**
```json
{
  "message": "PDF uploaded successfully",
  "doc_id": "58740b7f-eca7-4c8a-a308-bca9d928e5c7"
}
```

### Step 2: The Calibration Ritual (Latency Masking)

**Goal:** Buy time for the backend (Marker + LLM) to process the PDF.

**Visuals:** Full-screen overlay. Black background, high contrast.

**Interaction:**
- 9-point calibration grid appears sequentially.
- User must fixate on each dot until it "explodes" or changes color.

**System State (Hidden):** The frontend is polling the backend (`GET /api/get_pdf/{doc_id}`) every 1s.

**Exit Condition:**
- **Scenario A (Fast Processing):** Calibration finishes → Immediate fade to Reader.
- **Scenario B (Slow Processing):** Calibration finishes → Show a sophisticated "Finalizing Neural Analysis..." spinner (only for the remaining seconds).

**Polling Response:**
```json
// Processing
{ "status": "processing" }

// Ready
{
  "status": "success",
  "data": { /* DocumentResponse */ }
}
```

### Step 3: The Immersive Reader

**Layout:** Single column, distraction-free. Max-width 720px.

**The Canvas:** The text is the UI. No heavy toolbars.

**Feedback:** A subtle, semi-transparent "Gaze Orb" tracks the user's eye position (or mouse fallback) to confirm system responsiveness.

**Routes:** `/upload` → `/calibrate` → `/read`

---

## 2. Visual System & Typography

### Typography Hierarchy

Distinguish clearly between Content (the PDF text) and Meta-Data (AI insights).

**Body Text:** Georgia or Merriweather (Serif). High readability, leading-loose (2.0 line height).

**UI Elements / Marginalia:** Inter or system-ui (Sans-Serif). Clean, modern.

**Block Types:**

| Type | Style |
|------|-------|
| Headings | Bold, distinct margin-top |
| Paragraphs | Standard text, text-justify |
| Lists | Standard bullets, indented |
| Captions | Italic, gray text, centered below images |

### Color Semantics (The Highlight Engine)

We use a Multi-layer Overlay System. Colors carry semantic meaning. Opacity is key to maintaining readability.

| Element | Color | Opacity | Semantic Meaning |
|---------|-------|---------|------------------|
| Topic Sentence | Yellow (#FDE047) | 30% BG | "The core idea." Skimmable anchor. |
| SVO: Subject | Blue (#3B82F6) | Underline | "The Actor." Who is doing it? |
| SVO: Verb | Red (#F87171) | 20% BG | "The Action." What is happening? |
| SVO: Object | Green (#22C55E) | Underline | "The Target." To whom/what? |
| Anchors | Blue Dashed | 1px Stroke | Interactive keyword (Trigger Marginalia). |

**Implementation:** z-index overlay with coordinate-based rendering (Canvas), not DOM manipulation.

---

## 3. The Two Cognitive Modes

The user can toggle between these modes using the **S** (Skim) and **I** (Intensive) keys. The transition must be animated (`transition-all duration-300`).

### Mode A: Skim Mode (Structure-First)

**User Intent:** "I want to understand the skeleton of the argument quickly."

**Visual Behavior:**
- Non-essential text: Low contrast. Blur effect (`blur(0.5px)`), Opacity 0.4.
- Topic Sentences: Fully opaque (1.0), Yellow background active.
- SVO Syntax: Visible. Helps user parse complex sentence structures instantly.

**Experience:** X-Ray vision for text. The user scans down the page, only stopping at highlighted structures.

### Mode B: Intensive Mode (Detail-First)

**User Intent:** "I want to understand the specifics and vocabulary."

**Visual Behavior:**
- All text: Fully opaque (1.0). Sharp.
- Highlights: Topic/SVO highlights fade out or become very subtle.
- Interactive Anchors: Become active. Blue dashed underlines appear under technical terms.

---

## 4. Backend Architecture

### Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Python FastAPI |
| PDF Processing | Marker (PyTorch-based, outputs JSON) |
| LLM | Google Gemini API |
| Storage | File system (`data/uploads/`, `data/artifacts/`) |

### Pipeline Flow

```
PDF Upload → Marker CLI → JSON Extraction → LLM Enrichment → content.json
     ↓            ↓              ↓               ↓
 uploads/    artifacts/     parse children   add annotations
 {uuid}.pdf  {uuid}/        extract text     (topic, SVO, anchors)
```

### Directory Structure

```
backend/
├── main.py          # FastAPI app, API endpoints
├── pipeline.py      # PDF processing pipeline
├── llm.py           # Gemini LLM integration
├── schemas.py       # Pydantic models
└── requirements.txt

data/
├── uploads/         # Uploaded PDFs ({uuid}.pdf)
└── artifacts/       # Processed results
    └── {uuid}/
        ├── {uuid}.json       # Raw marker output
        ├── {uuid}_meta.json  # Marker metadata
        └── content.json      # Final enriched content (API response)
```

### Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash  # optional, default: gemini-2.5-flash
```

### Data Schema

```python
class SVOStructure(TypedDict):
    subject: Tuple[int, int]  # [start, end]
    verb: Tuple[int, int]
    object: Tuple[int, int]

class BilingualAnchor(BaseModel):
    term: str
    range: Tuple[int, int]
    translation: str
    nuance_note: Optional[str]
    trigger_threshold_ms: Optional[int] = 800

class BlockAnnotations(BaseModel):
    topic_sentence_range: Optional[Tuple[int, int]]
    svo_structure: Optional[Dict[str, Tuple[int, int]]]
    bilingual_anchors: Optional[List[BilingualAnchor]]

class Block(BaseModel):
    id: str
    type: str  # 'heading' | 'paragraph' | 'list-item' | 'caption' | 'image'
    content: str
    annotations: Optional[BlockAnnotations]

class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    meta: Optional[DocumentMeta]
    blocks: List[Block]
```

---

## 5. Frontend Architecture

### Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Vite + React 19 + TypeScript |
| State Management | Zustand |
| Styling | Tailwind CSS + clsx + tailwind-merge |
| Eye Tracking | Pupil Labs WebSocket |

### Directory Structure

```
frontend/src/
├── api/
│   └── client.ts             # API + Polling logic
├── components/
│   ├── Reader/
│   │   ├── Canvas.tsx        # Main reading canvas
│   │   ├── Block.tsx         # Block renderer
│   │   ├── HighlightOverlay.tsx # Multi-layer highlight engine (Canvas)
│   │   └── Marginalia.tsx    # Sidebar annotations
│   ├── EyeTracker/
│   │   ├── CalibrationTags.tsx  # 4-corner AprilTags
│   │   ├── GazeIndicator.tsx    # Gaze/mouse indicator
│   │   ├── GazeLogger.tsx       # Gaze data recorder
│   │   └── PupilLabsProvider.tsx
│   ├── Upload/
│   │   └── UploadForm.tsx
│   └── Calibration/
│       └── CalibrationPage.tsx
├── hooks/
│   ├── useGazePosition.ts    # Gaze position + Kalman filter
│   └── useTextRangeRect.ts   # Character position calculation
├── stores/
│   └── useReadingState.ts    # SKIM/INTENSIVE mode
└── App.tsx                   # Routes: /upload -> /calibrate -> /read
```

---

## 6. Interaction Design (IxD)

### The Marginalia (Side Notes)

**Trigger:** Gaze Dwell (800ms) or Mouse Hover on an Anchor (Intensive Mode).

**Animation:** Slides in from the right (`translateX`).

**Content:**
- Term: Bold.
- Translation: Secondary color.
- Nuance Note: Small text, explaining context.

**Placement:** Absolute positioned to the right of the paragraph, avoiding layout shifts (Reflow).

### Gaze Feedback (The "Ghost")

**Visual:** A ~40px circle.

**Style:** `backdrop-filter: invert(10%)` or subtle shadow. No solid colors (too distracting).

**Smoothing:** Apply a Kalman Filter (via `useGazePosition` hook) to remove jitter. The movement should feel liquid, not robotic.

**Parameters:**
- Q (Process Noise): 1e-5
- R (Measurement Noise): 0.01

### Eye Tracking Integration

**Pupil Labs Surface Tracking:**
- **Markers:** AprilTag 36h11 family (IDs 0-3) at 4 screen corners
- **WebSocket:** Connect to Pupil Companion App (`ws://<ip>:8080`)
- **Data:** Subscribe to surface topic for normalized coordinates (norm_x, norm_y)

**Fallback:** If eye tracker not connected, use mouse position.

### Gaze Logger (Invisible UX)

**Behavior:** The system silently logs "Dwell Time" per block.

**Performance:** Do not block the main thread. Data is batched and sent via Beacon API on page exit or periodically. The user should never feel a "save stutter."

```typescript
// Every 100ms, increment counter for current block
logRef.current[currentBlockId] += 100;

// On page unload, send via sendBeacon
navigator.sendBeacon('/api/analytics/gaze', JSON.stringify(logRef.current));
```

---

## 7. Technical UX Constraints

### Responsiveness

**Canvas Resize:** If the window resizes, the Highlight Overlay must recalculate coordinates immediately.

**Images:** Images must fit the column width (`w-full`, `h-auto`). Captions must stay attached to their images.

### Development Notes

**Mock Mode:**
```typescript
const MOCK_DOC_ID = "58740b7f-eca7-4c8a-a308-bca9d928e5c7";
const MOCK_MODE = true;
```

**Marker CLI:**
```bash
marker_single input.pdf --output_dir ./output --output_format json
```

**LLM Enrichment:** Processes in batches of 10 blocks. If a batch fails (e.g., invalid JSON), falls back to original blocks without annotations.

---

## 8. Implementation Checklist for Design Review

- [ ] **Latency Masking:** Does the calibration flow feel natural, or does it feel like a stalling tactic?
- [ ] **Color Blindness:** Are the Red/Green SVO indicators distinguishable by shape (Background vs Underline) in addition to color?
- [ ] **Readability:** Is the text legible under the Yellow/Red backgrounds? (Adjust opacity if needed).
- [ ] **Gaze Jitter:** Is the gaze indicator stable enough to read, or is it jumping around? (Tune Kalman filter Q/R values).
- [ ] **Highlight Accuracy:** Do the coordinate-based highlights align correctly with text after window resize?
- [ ] **Marginalia Animation:** Does the sidebar slide-in feel smooth without causing layout shifts?
