# Design Guidelines: Video Split & Merge Web App

## Design Approach

**Selected Framework**: Hybrid approach combining Notion's clean productivity aesthetic with Duolingo's gamification elements. Mobile-first design prioritizing touch interactions, clear visual feedback, and progress visualization.

**Core Principles**:
- Touch-optimized UI (minimum 44px tap targets)
- Instant visual feedback for all actions
- Progressive disclosure of complexity
- Achievement-based motivation system

## Typography

**Font Family**: 
- Primary: 'Inter' (Google Fonts) - clean, readable at small sizes
- Accent: 'Poppins' SemiBold for gamification elements

**Hierarchy**:
- H1: text-2xl font-bold (main page titles)
- H2: text-xl font-semibold (section headers)
- H3: text-lg font-medium (card titles)
- Body: text-base (primary content)
- Small: text-sm (helper text, metadata)
- Tiny: text-xs (badges, timestamps)

## Layout System

**Spacing Units**: Tailwind units of 2, 4, 6, and 8
- Component padding: p-4 or p-6
- Section spacing: space-y-4 or space-y-6
- Card gaps: gap-4
- Screen padding: px-4 (mobile), px-6 (tablet+)

**Container Strategy**:
- Mobile: Full width with px-4 padding
- Tablet+: max-w-4xl centered
- Single-column priority, cards stack vertically

## Component Library

### Core Navigation
**Bottom Navigation Bar** (fixed, mobile-optimized):
- 3 primary actions: Upload, Split, Merge
- Large icons (w-6 h-6) with labels
- Active state with indicator bar above icon
- Height: h-16 with safe area padding

### Upload Interface
**Drag & Drop Zone**:
- Large touch area (min-h-48 on mobile)
- Dashed border (border-2 border-dashed)
- Central upload icon and text
- File input button: Large, rounded-xl, w-full on mobile

### Video Management Cards
**Video Item Card**:
- Thumbnail preview (aspect-video, rounded-lg)
- Video filename (truncated with ellipsis)
- Duration badge (absolute positioned, top-right, rounded-full)
- Action buttons row: Delete, Preview, Select
- Card spacing: p-4, rounded-xl, touch-friendly gaps

### Split Configuration Panel
**Time Input Controls**:
- Large number stepper (increment/decrement buttons w-12 h-12)
- Center display showing seconds (text-3xl font-bold)
- Quick preset buttons below (5s, 10s, 30s, 60s) as rounded-full pills
- Visual segment preview showing how many parts will be created

### Progress Visualization
**Gamification Elements**:
- Circular progress rings for processing status
- XP bar showing "videos processed" achievement
- Achievement badges (rounded-full icons with counts)
- Success animations using simple scale/fade transitions

### Action Buttons
**Primary Actions** (CTAs):
- Full width on mobile: w-full rounded-xl h-12
- Clear labels with icons: "Split Video", "Merge Videos"
- Loading states with spinner replacement

**Secondary Actions**:
- Outlined style: border-2 rounded-xl
- Same height as primary (h-12)

### Processing States
**Status Cards**:
- Processing: Animated progress bar with percentage
- Queue display: List of pending operations
- Success state: Checkmark icon with download button
- Error state: Alert icon with retry option

### Video Preview Modal
**Overlay Interface**:
- Full-screen on mobile (fixed inset-0)
- Video player centered with controls
- Close button (top-right, w-10 h-10, rounded-full)
- Swipe-to-dismiss gesture support

### Merge Interface
**Reorder List**:
- Drag handles (visible grip icons)
- Video thumbnails in sequence
- Order numbers (large, circular badges)
- Rearrange with touch-hold and drag
- Preview button showing final timeline

## Gamification Features

**Achievement System**:
- Badge collection grid (3-column on mobile)
- Unlock animations for milestones
- Progress toward next achievement
- Stats dashboard: Total videos processed, time saved, largest project

**Visual Rewards**:
- Confetti burst on successful merge (subtle, 1-2 second)
- Progress level-up notification
- Streak counter for consecutive days used

## Mobile Interactions

**Gestures**:
- Swipe to delete video from list
- Pull-to-refresh for video library
- Long-press for additional options menu
- Pinch-to-zoom on video thumbnails (preview)

**Touch Optimization**:
- All interactive elements minimum 44px height
- Adequate spacing between tap targets (gap-3 minimum)
- Clear pressed states (scale-95 on active)

## Responsive Behavior

**Mobile (default)**:
- Single column layouts
- Bottom navigation
- Full-width cards
- Stacked buttons

**Tablet (md: 768px+)**:
- Two-column grid for video library
- Side navigation option
- Max width container (max-w-4xl)
- Button groups horizontal

**Desktop (lg: 1024px+)**:
- Three-column video grid
- Persistent sidebar
- Hover states enabled
- Keyboard shortcuts support

## Images

No hero images required - this is a utility application. Images used are:
- Video thumbnails (generated from uploaded videos)
- Achievement badge icons (use icon library)
- Empty state illustrations (simple line-art SVG from icon library)