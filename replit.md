# VideoSplit - Video Split & Merge Web Application

## Overview

VideoSplit is a mobile-first web application for splitting and merging video files. Users can upload videos, split them into segments of configurable duration, or merge multiple videos into one. The app features a gamification layer with achievements and statistics tracking to enhance user engagement.

The application follows a monorepo structure with a React frontend and Express backend, using FFmpeg for video processing operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight React router)
- **State Management**: TanStack React Query for server state
- **UI Components**: shadcn/ui component library built on Radix UI primitives
- **Styling**: Tailwind CSS with CSS variables for theming (light/dark mode support)
- **Build Tool**: Vite with hot module replacement

**Design Philosophy**: Mobile-first approach with touch-optimized UI (44px minimum tap targets), bottom navigation bar, and gamification elements inspired by Duolingo's achievement system.

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Video Processing**: FFmpeg via fluent-ffmpeg library
- **File Uploads**: Multer middleware with disk storage
- **Storage**: In-memory storage for video metadata and job tracking (MemStorage class)
- **API Design**: RESTful endpoints under `/api/` prefix

**Key Endpoints**:
- `POST /api/videos/upload` - Upload video files
- `POST /api/videos/split` - Split video into segments
- `POST /api/videos/merge` - Merge multiple videos
- `GET /api/videos` - List uploaded videos
- `GET /api/jobs` - Track processing jobs
- `GET /api/stats` - User statistics

### Data Storage
- **Current**: In-memory storage using Map structures (non-persistent)
- **Database Ready**: Drizzle ORM configured with PostgreSQL dialect
- **Schema**: Zod schemas defined in `shared/schema.ts` for validation
- **File Storage**: Local filesystem (`uploads/` and `outputs/` directories)

### Build System
- **Development**: Vite dev server with Express API proxy
- **Production**: esbuild bundles server code, Vite builds client assets
- **Output**: Single `dist/` directory with `index.cjs` (server) and `public/` (static assets)

## External Dependencies

### Video Processing
- **FFmpeg**: System-level dependency required for video splitting and merging operations. Uses `fluent-ffmpeg` Node.js wrapper.

### Database (Configured but Optional)
- **PostgreSQL**: Drizzle ORM configuration present for future database integration
- **Environment Variable**: `DATABASE_URL` required when database features are enabled

### Third-Party Services
- None currently integrated. The application operates entirely locally.

### Key NPM Dependencies
- `@tanstack/react-query` - Server state management
- `fluent-ffmpeg` - FFmpeg Node.js bindings
- `multer` - File upload handling
- `drizzle-orm` / `drizzle-zod` - Database ORM (prepared for use)
- `wouter` - Client-side routing
- Radix UI primitives - Accessible UI components