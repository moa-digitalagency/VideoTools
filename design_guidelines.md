# Video Processing App - Design Guidelines

## Design Approach
**Reference**: Blend Capcut's video-focused UI + Telegram's clean interface hierarchy + modern app aesthetics. Utility-first with delightful visual touches.

## Typography
- **Primary Font**: Inter (Google Fonts) - exceptional clarity for UI
- **Headings**: 700 weight, tight tracking (-0.02em)
- **Body**: 400/500 weight, relaxed line-height (1.6)
- **Buttons/Labels**: 600 weight, uppercase for primary actions
- **Size Scale**: text-sm (mobile nav/labels), text-base (body), text-lg (section headers), text-2xl/3xl (page titles), text-4xl (hero)

## Layout System
**Spacing Units**: Tailwind 3, 4, 6, 8, 12, 16 for consistent rhythm
- Mobile: p-4, gap-4 (components), py-8 (sections)
- Desktop: p-6/8, gap-6, py-16 (sections)
- Max widths: max-w-md (mobile-first), max-w-4xl (desktop)

## Core Components

### Navigation
**Mobile Bottom Nav** (sticky):
- 4 icons: Upload, Process, Downloads, Profile
- Active state: icon + label, inactive: icon only
- Floating style with backdrop-blur, rounded-2xl, shadow-lg
- 56px height, safe-area padding

**Desktop Top Nav**:
- Logo left, features center, account/CTA right
- Transparent with blur on scroll, h-16

### Hero Section
**Layout**: Full-screen mobile (90vh), 70vh desktop
**Image**: Abstract tech visualization - flowing blue data streams, video frames in motion, glowing particles. Conveys speed and processing power
**Content**: 
- Centered overlay with backdrop-blur card
- Headline + 2-line description + dual CTAs (Upload Video, Learn More)
- Lottie animation: Floating video player icon with pulse effect

### Video Upload Card
**Style**: Prominent dashed border, rounded-3xl, min-h-48
- Drag-drop zone with Lottie upload animation (cloud → check)
- File specs below: "MP4, MOV up to 500MB"
- Progress bar: gradient fill, rounded-full, smooth transitions

### Processing Interface
**Tool Cards Grid**: 
- Mobile: Single column, gap-4
- Desktop: 2-column, gap-6
- Each card: Icon (Lottie), title, description, action button
- Tools: Split Video, Merge Clips, TikTok Downloader, Trim/Cut
- Hover: lift effect (transform scale-105), glow border

### Action Buttons
**Primary**: Rounded-full, px-8 py-4, font-semibold, shadow-xl
**On Images**: backdrop-blur-md, semi-transparent background, NO hover blur changes
**Secondary**: Outlined, border-2, rounded-full

### Timeline/Editor Preview
**Split Feature**: Draggable markers on timeline
- Waveform visualization background
- Snap-to-grid feedback
- Lottie scissor animation on split points

### Results Display
**Video Cards**: 
- Thumbnail + metadata overlay
- Download button, share options
- Processing status with animated spinner (Lottie)

## Lottie Animations
**Strategic Placement**:
1. Hero: Looping ambient effect (subtle)
2. Upload success: Bouncy checkmark (0.8s)
3. Processing: Circular progress indicator
4. Feature icons: Micro-interactions on tap (0.3s)
**Rule**: Maximum 3 concurrent animations, prioritize performance

## Images
**Hero**: Large abstract tech image as described above - essential for visual impact
**Feature Icons**: Use Heroicons via CDN for tool buttons
**Video Thumbnails**: Placeholder grid pattern for empty states

## Responsive Strategy
**Mobile**: Single column, sticky bottom nav, full-width cards
**Tablet**: 2-column grids, top nav appears
**Desktop**: Max-width containers, 3-column feature grids, persistent sidebar for tools

**Viewport Heights**: Natural content flow except hero (90vh mobile, 70vh desktop)