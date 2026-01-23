# Cognitive Reader: UX Design Specification

**Version:** 2.0
**Target Audience:** Design & Engineering Team
**Last Updated:** 2025-01-23

---

## Core Philosophy

> **"Augmented Reading"** — Using gaze data to manage cognitive load, not just track it.

The system transforms passive reading into an active, adaptive experience where visual feedback guides attention and comprehension.

---

## 1. The User Journey (The "Masking" Workflow)

We are implementing a specific **"Ritual"** to hide backend processing time (30s-60s). The user must perceive this as a necessary calibration step, not a loading screen.

### Step 1: Entry & Upload

**Interface:** Clean, minimal dropzone.

**Visual Design:**
- Centered dropzone with dashed border
- Subtle hover state (border color change)
- No distracting elements or excessive branding

**Interaction:** Drag & drop PDF.

**Feedback:** Immediate transition to Step 2 upon file release. **No "Uploading..." bar**; jump straight to the "Ritual."

**Technical Flow:**
```
User drops PDF → POST /api/upload_pdf → Receive doc_id → Navigate to /calibrate
```

**Error Handling:**
- Invalid file type: Show inline error, allow retry
- Upload failure: Display error message, return to dropzone

---

### Step 2: The Calibration Ritual (Latency Masking)

**Goal:** Buy time for the backend (Marker + LLM) to process the PDF.

**Visuals:** Full-screen overlay. Black background (`#000000`), high contrast.

**Calibration Grid:**
- **Layout:** 3x3 grid (9 points)
- **Appearance:** White dots (`#FFFFFF`) on black background
- **Size:** ~20px diameter
- **Spacing:** Evenly distributed across viewport

**Interaction Sequence:**
1. First dot appears at center
2. User must fixate on dot until it "explodes" or changes color
3. Success feedback: Dot expands → fades → next dot appears
4. Repeat for all 9 points
5. Estimated duration: 15-30 seconds

**Visual Feedback:**
- **Active dot:** Pulsing animation, slight scale increase
- **Completed dot:** Green checkmark overlay, fade out
- **Progress indicator:** Subtle progress bar at bottom (optional)

**System State (Hidden):** The frontend is polling the backend (`GET /api/get_pdf/{doc_id}`) every 1s.

**Exit Condition:**

| Scenario | Condition | Behavior |
|----------|-----------|----------|
| **A: Fast Processing** | Calibration finishes + Data ready | Immediate fade to Reader (no delay) |
| **B: Slow Processing** | Calibration finishes + Data not ready | Show sophisticated "Finalizing Neural Analysis..." spinner with animated progress indicator |

**Loading State (Scenario B):**
- **Message:** "Finalizing Neural Analysis..."
- **Visual:** Subtle animated gradient or particle effect
- **Duration:** Only for remaining seconds (typically 0-30s)
- **Style:** Minimal, non-intrusive, maintains black background aesthetic

---

### Step 3: The Immersive Reader

**Layout:** Single column, distraction-free. Max-width 720px, centered.

**The Canvas:** The text is the UI. No heavy toolbars.

**Visual Hierarchy:**
```
┌─────────────────────────────────────────┐
│  [Minimal Header: Title + Mode Toggle]   │ ← Optional, collapsible
├─────────────────────────────────────────┤
│                                         │
│  [Main Content: Blocks]                 │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Paragraph with highlights       │   │
│  │ and annotations                 │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Feedback:** A subtle, semi-transparent "Gaze Orb" tracks the user's eye position (or mouse fallback) to confirm system responsiveness.

**Navigation:**
- **Keyboard:** `S` (Skim mode), `I` (Intensive mode)
- **Scroll:** Smooth, native browser scrolling
- **No pagination:** Continuous scroll experience

---

## 2. Visual System & Typography

### Typography Hierarchy

Distinguish clearly between **Content** (the PDF text) and **Meta-Data** (AI insights).

#### Body Text

**Font:** Georgia or Merriweather (Serif)
**Size:** 18-20px (1.125rem - 1.25rem)
**Line Height:** 2.0 (`leading-loose`)
**Color:** `#1F2937` (near black)
**Weight:** 400 (regular)

**Rationale:** Serif fonts improve readability for long-form text. High line height reduces eye strain.

#### UI Elements / Marginalia

**Font:** Inter or system-ui (Sans-Serif)
**Size:** 14-16px (0.875rem - 1rem)
**Line Height:** 1.5
**Color:** `#6B7280` (gray-500)
**Weight:** 400-500

**Rationale:** Sans-serif provides clean, modern feel for UI elements and metadata.

### Block Types

| Type | Font | Size | Weight | Style | Spacing |
|------|------|------|--------|-------|---------|
| **Headings** | Serif | 2rem (32px) | 700 (bold) | Normal | `mt-8 mb-4` |
| **Paragraphs** | Serif | 1.25rem (20px) | 400 | Normal | `mb-6` |
| **Lists** | Serif | 1.25rem (20px) | 400 | Normal | `ml-8 mb-2` |
| **Captions** | Sans | 0.875rem (14px) | 400 | Italic | `mt-2 mb-8` |

**Code Example:**
```css
.heading {
  font-family: 'Merriweather', serif;
  font-size: 2rem;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.paragraph {
  font-family: 'Merriweather', serif;
  font-size: 1.25rem;
  line-height: 2.0;
  text-align: justify;
  margin-bottom: 1.5rem;
}

.caption {
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  font-style: italic;
  color: #6B7280;
  text-align: center;
}
```

---

### Color Semantics (The Highlight Engine)

We use a **Multi-layer Overlay System**. Colors carry semantic meaning. Opacity is key to maintaining readability.

| Element | Color | Hex | Opacity | Visual Style | Semantic Meaning |
|---------|-------|-----|---------|--------------|------------------|
| **Topic Sentence** | Yellow | `#FDE047` | 30% BG | Solid background | "The core idea." Skimmable anchor. |
| **SVO: Subject** | Blue | `#3B82F6` | 60% | Underline (2px) | "The Actor." Who is doing it? |
| **SVO: Verb** | Red | `#F87171` | 20% BG | Solid background | "The Action." What is happening? |
| **SVO: Object** | Green | `#22C55E` | 60% | Underline (2px) | "The Target." To whom/what? |
| **Anchors** | Blue | `#3B82F6` | 80% | Dashed underline (1px) | Interactive keyword (Trigger Marginalia). |

**Implementation Notes:**
- All highlights use **z-index overlay** (Canvas-based), not DOM manipulation
- Colors are applied in **Painter's Algorithm** order (bottom to top):
  1. Topic Sentence (background)
  2. SVO Subject (underline)
  3. SVO Verb (background)
  4. SVO Object (underline)
  5. Anchors (dashed underline)

**Accessibility:**
- Red/Green SVO indicators are distinguishable by **shape** (Background vs Underline) in addition to color
- All colors meet WCAG AA contrast ratios when overlaid on text

---

## 3. The Two Cognitive Modes

The user can toggle between these modes using the **S** (Skim) and **I** (Intensive) keys. The transition must be animated (`transition-all duration-300`).

### Mode A: Skim Mode (Structure-First)

**User Intent:** "I want to understand the skeleton of the argument quickly."

**Visual Behavior:**

| Element | Opacity | Blur | Other Effects |
|---------|---------|------|---------------|
| Non-essential text | 0.4 | `blur(0.5px)` | Reduced contrast |
| Topic Sentences | 1.0 | None | Yellow background active |
| SVO Syntax | 1.0 | None | Color-coded underlines/backgrounds |
| Anchors | 0.4 | `blur(0.5px)` | Inactive |

**Experience:** X-Ray vision for text. The user scans down the page, only stopping at highlighted structures.

**Use Cases:**
- First pass through a document
- Finding main arguments
- Quick comprehension check

**Animation:**
```css
.skim-mode .non-topic {
  opacity: 0.4;
  filter: blur(0.5px);
  transition: all 0.3s ease;
}

.skim-mode .topic-sentence {
  opacity: 1;
  font-weight: 600;
  transition: all 0.3s ease;
}
```

---

### Mode B: Intensive Mode (Detail-First)

**User Intent:** "I want to understand the specifics and vocabulary."

**Visual Behavior:**

| Element | Opacity | Blur | Other Effects |
|---------|---------|------|---------------|
| All text | 1.0 | None | Full contrast, sharp |
| Topic/SVO highlights | 0.1-0.2 | None | Very subtle (fade out) |
| Interactive Anchors | 1.0 | None | Blue dashed underlines active |

**Experience:** Full detail mode. User focuses on technical terms and nuanced explanations.

**Use Cases:**
- Deep reading
- Vocabulary learning
- Technical comprehension

**Animation:**
```css
.intensive-mode .text {
  opacity: 1;
  filter: none;
  transition: all 0.3s ease;
}

.intensive-mode .anchor {
  border-bottom: 1px dashed #3B82F6;
  transition: all 0.3s ease;
}
```

---

## 4. Interaction Design (IxD)

### The Marginalia (Side Notes)

**Trigger:** Gaze Dwell (800ms) or Mouse Hover on an Anchor (Intensive Mode).

**Animation:** Slides in from the right (`translateX`).

**Timing:**
- **Enter:** 300ms ease-out
- **Exit:** 200ms ease-in
- **Delay:** 800ms after trigger (gaze dwell threshold)

**Content Structure:**
```
┌─────────────────────────────┐
│ Term (Bold, 16px)           │
│ Translation (Secondary, 14px)│
│ ─────────────────────────── │
│ Nuance Note (Small, 12px)   │
│ (2-3 sentences max)         │
└─────────────────────────────┘
```

**Visual Design:**
- **Background:** White (`#FFFFFF`) with subtle shadow
- **Border:** 1px solid `#E5E7EB` (gray-200)
- **Padding:** 16px
- **Max Width:** 280px
- **Border Radius:** 8px

**Placement:** Absolute positioned to the right of the paragraph, avoiding layout shifts (Reflow).

**Code Example:**
```css
.marginalia {
  position: absolute;
  right: -300px;
  top: 0;
  width: 280px;
  padding: 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateX(0);
  transition: transform 0.3s ease-out;
}

.marginalia.active {
  transform: translateX(-320px); /* Slide into view */
}
```

**Behavior:**
- Only one Marginalia visible at a time
- Clicking outside or moving gaze away closes it
- Smooth fade-in/fade-out transitions

---

### Gaze Feedback (The "Ghost")

**Visual:** A ~40px circle.

**Style:** `backdrop-filter: invert(10%)` or subtle shadow. No solid colors (too distracting).

**Design Specs:**
- **Size:** 40px diameter
- **Border:** 2px solid `rgba(59, 130, 246, 0.3)` (blue, semi-transparent)
- **Background:** `rgba(255, 255, 255, 0.1)` (white, very transparent)
- **Shadow:** `0 0 20px rgba(59, 130, 246, 0.2)` (blue glow)
- **Backdrop Filter:** `invert(10%) blur(2px)` (optional)

**Smoothing:** Apply a Kalman Filter (via `useGazePosition` hook) to remove jitter. The movement should feel liquid, not robotic.

**Kalman Filter Parameters:**
- **Q (Process Noise):** 1e-5
- **R (Measurement Noise):** 0.01
- **Update Rate:** 60fps (16.67ms intervals)

**Code Example:**
```typescript
// useGazePosition.ts
const kalmanFilter = {
  Q: 1e-5,  // Process noise
  R: 0.01,  // Measurement noise
  x: 0,     // State estimate
  P: 1,     // Error covariance
};

function filterGaze(rawX: number, rawY: number) {
  // Apply 1D Kalman filter to X and Y independently
  // Return smoothed { x, y }
}
```

**Fallback:** If eye tracker not connected, use mouse position with same visual style.

---

## 5. Technical UX Constraints

### Data Logging (Invisible UX)

**Behavior:** The system silently logs "Dwell Time" per block.

**Performance:** Do not block the main thread. Data is batched and sent via Beacon API on page exit or periodically. The user should never feel a "save stutter."

**Implementation:**
```typescript
// GazeLogger.tsx
const logRef = useRef<Record<string, number>>({});

// Every 100ms, increment counter for current block
useInterval(() => {
  if (currentBlockId) {
    logRef.current[currentBlockId] = (logRef.current[currentBlockId] || 0) + 100;
  }
}, 100);

// On page unload, send via sendBeacon
useEffect(() => {
  return () => {
    const data = JSON.stringify(logRef.current);
    navigator.sendBeacon('/api/analytics/gaze', data);
  };
}, []);
```

**Data Format:**
```json
{
  "doc_id": "58740b7f-eca7-4c8a-a308-bca9d928e5c7",
  "fixations": {
    "/page/0/Text/2": 2500,  // milliseconds
    "/page/0/Text/3": 1800,
    "/page/0/SectionHeader/1": 500
  }
}
```

---

### Responsiveness

**Canvas Resize:** If the window resizes, the Highlight Overlay must recalculate coordinates immediately.

**Implementation:**
```typescript
// HighlightOverlay.tsx
useEffect(() => {
  const handleResize = () => {
    // Recalculate all highlight rectangles
    recalculateHighlights();
  };

  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

**Images:** Images must fit the column width (`w-full`, `h-auto`). Captions must stay attached to their images.

**Responsive Breakpoints:**
- **Mobile (< 640px):** Single column, full width
- **Tablet (640px - 1024px):** Max-width 720px, centered
- **Desktop (> 1024px):** Max-width 720px, centered, with side margins

---

## 6. Implementation Checklist for Design Review

### Latency Masking

- [ ] Does the calibration flow feel natural, or does it feel like a stalling tactic?
- [ ] Is the 9-point calibration engaging enough to mask 30-60s processing time?
- [ ] Does the "Finalizing Neural Analysis..." message feel sophisticated, not generic?

### Color & Accessibility

- [ ] Are the Red/Green SVO indicators distinguishable by shape (Background vs Underline) in addition to color?
- [ ] Do all color combinations meet WCAG AA contrast ratios?
- [ ] Is the text legible under the Yellow/Red backgrounds? (Adjust opacity if needed)

### Gaze Tracking

- [ ] Is the gaze indicator stable enough to read, or is it jumping around? (Tune Kalman filter Q/R values)
- [ ] Does the "Ghost" orb feel responsive and natural?
- [ ] Is the fallback to mouse position seamless?

### Highlight Accuracy

- [ ] Do the coordinate-based highlights align correctly with text after window resize?
- [ ] Are multi-line highlights rendered correctly?
- [ ] Do highlights update smoothly when switching between Skim/Intensive modes?

### Interaction Polish

- [ ] Does the Marginalia slide-in feel smooth without causing layout shifts?
- [ ] Is the 800ms gaze dwell threshold appropriate? (Not too fast, not too slow)
- [ ] Do keyboard shortcuts (S/I) feel responsive and intuitive?

### Performance

- [ ] Is the highlight overlay rendering performant? (60fps target)
- [ ] Does data logging cause any UI stutter?
- [ ] Are images loading and displaying correctly?

---

## 7. Design Tokens

### Colors

```css
/* Semantic Colors */
--color-topic: #FDE047;      /* Yellow */
--color-subject: #3B82F6;    /* Blue */
--color-verb: #F87171;       /* Red */
--color-object: #22C55E;     /* Green */
--color-anchor: #3B82F6;     /* Blue */

/* Neutral Colors */
--color-text-primary: #1F2937;   /* Gray-800 */
--color-text-secondary: #6B7280; /* Gray-500 */
--color-bg-primary: #FFFFFF;
--color-bg-overlay: #000000;

/* Opacity Values */
--opacity-topic-bg: 0.3;
--opacity-verb-bg: 0.2;
--opacity-underline: 0.6;
```

### Spacing

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;       /* 32px */

--max-width-content: 720px;
--gutter: 1rem;
```

### Typography

```css
--font-serif: 'Merriweather', 'Georgia', serif;
--font-sans: 'Inter', system-ui, sans-serif;

--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-base: 1rem;    /* 16px */
--font-size-lg: 1.25rem;   /* 20px */
--font-size-xl: 2rem;      /* 32px */

--line-height-tight: 1.5;
--line-height-normal: 2.0;
```

### Animation

```css
--transition-fast: 0.2s ease-in;
--transition-normal: 0.3s ease-out;
--transition-slow: 0.4s ease;

--duration-gaze-dwell: 800ms;
--duration-marginalia-enter: 300ms;
--duration-marginalia-exit: 200ms;
```

---

## 8. Future Enhancements

### Phase 2 Features

- [ ] **Review Generator:** Generate personalized summaries based on gaze data
- [ ] **Reading Analytics Dashboard:** Visualize reading patterns and comprehension metrics
- [ ] **Custom Highlight Colors:** User-configurable color schemes
- [ ] **Export Annotations:** Save highlighted sections as notes
- [ ] **Multi-language Support:** Extend beyond English-Chinese bilingual anchors

### Research Questions

- What is the optimal gaze dwell threshold for triggering Marginalia?
- How does SVO highlighting affect reading comprehension?
- Does the "Masking Ritual" actually improve perceived performance?

---

**Document Status:** Living Document — Updated as implementation progresses.
