# LiftLink — 3D UI Enhancement Product Requirements Document (PRD)

| Field | Value |
|-------|-------|
| **Product Name** | LiftLink 3D UI Enhancement |
| **Version** | 1.0.0 (Semester 6 — Academic Minor Project) |
| **Document Status** | Draft for Review |
| **Last Updated** | 2026-05-26 |
| **Primary Audience** | Developers, UI/UX Designers, AI coding assistants |
| **Platform** | Responsive Web Application (PWA), mobile-first |
| **Institution Scope** | Parul University students and staff only |

---

## Table of Contents

1. [Introduction & Objectives](#1-introduction--objectives)
2. [Scope of 3D UI](#2-scope-of-3d-ui)
3. [Technology Stack for 3D](#3-technology-stack-for-3d)
4. [User Flows & Interactions](#4-user-flows--interactions)
5. [Component Specifications](#5-component-specifications)
6. [Performance & Accessibility](#6-performance--accessibility)
7. [Implementation Plan](#7-implementation-plan)
8. [Future Scope](#8-future-scope)

---

## 1. Introduction & Objectives

### 1.1 Product Vision

Enhance the existing LiftLink PWA with a 3D UI layer that provides depth, interactivity, and a modern aesthetic while maintaining usability and performance. The 3D elements should improve user engagement without compromising the core functionality of ride-pooling.

### 1.2 Problem Statement

The current 2D UI, while functional, lacks visual depth and interactive feedback that could improve user experience. Buttons and cards feel flat, and there's limited visual hierarchy to guide users through the ride-booking process.

### 1.3 Target Users

Same as the base LiftLink application: Riders and Drivers within the Parul University community.

### 1.4 Semester 6 Objectives (In Scope)

| ID | Objective | Success Metric |
|----|-----------|----------------|
| O1 | Implement 3D buttons with hover/press feedback | 90% of users notice and interact with 3D buttons in usability testing |
| O2 | Create 3D ride cards for offers and requests | Increased click-through rate on ride cards by 20% |
| O3 | Add subtle 3D depth to map containers and modals | Users report improved sense of spatial relationships |
| O4 | Maintain performance targets (<100ms interaction latency) | 95th percentile interaction time <100ms on mid-tier devices |
| O5 | Ensure accessibility compliance (WCAG 2.1 AA) | All 3D elements are keyboard navigable and screen reader friendly |

### 1.5 Explicit Non-Goals (Semester 6)

- Full 3D map rendering (keeping Leaflet 2D map for performance and familiarity)
- Complex 3D animations that distract from core tasks
- VR/AR headset support
- 3D avatars or character models

### 1.6 Assumptions & Constraints

- Users have devices capable of basic WebGL (most modern smartphones and browsers)
- Fallback to 2D UI for users with disabled WebGL or very low-end devices
- 3D enhancements should not increase bundle size by more than 50KB gzipped
- Maintain existing color scheme and typography from Tailwind configuration

---

## 2. Scope of 3D UI

The 3D UI will be applied to the following elements:

1. **Interactive Buttons** - Primary action buttons (Offer a Ride, Find a Ride, Search, Accept, Reject, Complete)
2. **Ride Cards** - Offer cards in search results and request cards in inbox
3. **Containers & Modals** - Dashboard widgets, form containers, confirmation modals
4. **Input Fields** - Search boxes and form inputs with subtle 3D depth
5. **Navigation Elements** - Tabs and bottom navigation (if implemented)

The Leaflet map will remain 2D but will be placed within a 3D-enhanced container that provides subtle depth and shadow.

---

## 3. Technology Stack for 3D

### 3.1 Core Library

- **React Three Fiber** (latest) - React renderer for Three.js
- **@react-three/drei** - Useful helpers and abstractions for React Three Fiber
- **three** - Base 3D library

### 3.2 Why This Stack?

- Seamless integration with existing React/Vite setup
- Declarative approach matches React patterns
- Good performance with built-in instancing and frustum culling
- Active community and documentation
- Smaller bundle alternatives considered (like @dimforge/rapier3d) were rejected as overkill for UI

### 3.3 Installation

```bash
npm install three @react-three/fiber @react-three/drei
```

### 3.4 Fallback Strategy

- Use `useCanvas` from React Three Fiber to detect WebGL support
- Provide 2D fallback components that render identical UI without 3D effects
- Feature flag in context to disable 3D for performance-sensitive users

---

## 4. User Flows & Interactions

### 4.1 Button Interactions

All 3D buttons follow this interaction model:

1. **Rest State** - Slightly elevated with subtle shadow
2. **Hover** - Lifts upward 8px, increases shadow intensity, slight rotation on Y-axis (2 degrees)
3. **Press** - Moves downward 4px, reduces shadow, scales to 98%
4. **Focus** (keyboard) - Same as hover but with outline ring
5. **Disabled** - Flat, desaturated, no lift on hover

### 4.2 Ride Card Interactions

Ride cards in search results and inbox:

1. **Rest** - Flat card with subtle inner shadow
2. **Hover** - Lifts 12px, increases shadow, slight tilt based on cursor position
3. **Press** - Moves downward 6px
4. **Selected** (for multi-select scenarios) - Glowing outline and slight pulse animation
5. **Swipe** (on mobile) - Horizontal swipe reveals action buttons with 3D flip effect

### 4.3 Modal & Container Depth

- Modals appear with a 3D fade-in (scale from 95% to 100% while lifting 20px)
- Overlay has subtle 3D depth with blurred background
- Form inputs inside modals have inset shadow to appear pressed into the surface

### 4.4 Feedback Mechanisms

- **Sound** - Optional subtle click sound on button press (configurable in settings)
- **Haptic** - On supported mobile devices, light haptic feedback on button press
- **Visual** - Ripple effect on press (using CSS/JS, not WebGL for performance)

---

## 5. Component Specifications

### 5.1 3D Button Component (`Button3D`)

```tsx
interface Button3DProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  elevation?: number // 1-5, controls lift height
  tiltEnabled?: boolean
  children: React.ReactNode
}

// Usage:
// <Button3D variant="primary" size="lg" onClick={handleOfferRide}>
//   Offer a Ride
// </Button3D>
```

### 5.2 3D Ride Card Component (`RideCard3D`)

```tsx
interface RideCard3DProps {
  offer: OfferType // or RequestType
  onSelect: (offerId: string) => void
  onAction?: (action: string, offerId: string) => void
  isSelected?: boolean
  elevation?: number
  children?: React.ReactNode
}

// Displays:
// - Driver avatar with 3D ring
- Route origin/destination labels
- Fuel split cost badge
- Departure time
- Action buttons (Request/Accept/Reject)
```

### 5.3 3D Map Container (`MapContainer3D`)

Wraps the existing Leaflet map:

```tsx
interface MapContainer3DProps {
  children: React.ReactNode // Leaflet map element
  elevation?: number
  shadowIntensity?: number
}

// Provides:
// - 3D lifted container with drop shadow
- Subtle parallax effect on scroll
- Glow effect when map is interacted with
```

### 5.4 3D Input Field (`Input3D`)

```tsx
interface Input3DProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'filled' | 'outlined'
  size?: 'sm' | 'md' | 'lg'
  elevation?: number
  // All standard input props
}

// Features:
// - Inset shadow when focused
- Lifting label on focus (if applicable)
// - Underline animation on focus
```

---

## 6. Performance & Accessibility

### 6.1 Performance Targets

- **Initial Load** - 3D UI should not increase first contentful paint by more than 200ms
- **Interaction Latency** - 95th percentile <100ms for button presses
- **Frame Rate** - Maintain 60fps during interactions on mid-tier devices (Snapdragon 7xx/Apple A12 equivalent)
- **Memory** - Additional memory usage <50MB
- **Bundle Size** - <50KB gzipped for 3D dependencies

### 6.2 Optimization Techniques

- **Instancing** - For repeated elements (buttons in lists)
- **Frustum Culling** - Automatic in Three.js
- **Level of Detail** - Simpler shadows for distant UI elements
- **Texture Atlasing** - For UI icons if needed
- **Request Animation Frame** - Sync rendering with browser refresh
- **Web Worker** - Offload complex calculations if needed

### 6.3 Accessibility

- **Keyboard Navigation** - All 3D elements must be tab-navigable
- **Screen Reader** - ARIA labels preserved, no reliance on visual cues alone
- **Reduced Motion** - Respect `prefers-reduced-motion` media query (disable non-essential animations)
- **Color Contrast** - Maintain WCAG AA contrast ratios in all states
- **Focus Indicators** - Visible focus outlines for keyboard users
- **Touch Targets** - Minimum 44x44px interactive areas

### 6.4 Fallback Conditions

3D UI automatically falls back to 2D when:
- `navigator.gpu` is undefined (WebGPU not available) AND WebGL2 context creation fails
- Device reports low memory (<512MB RAM) via `navigator.deviceMemory`
- User has explicitly disabled animations in OS settings
- FPS drops below 30 for 2 consecutive seconds during interaction

---

## 7. Implementation Plan

### 7.1 Phase 1: Foundation (Week 1)

- [ ] Set up React Three Fiber environment
- [ ] Create basic 3D canvas provider with fallback mechanism
- [ ] Implement `Button3D` component with hover/press states
- [ ] Create 2D fallback versions of all 3D components
- [ ] Add performance monitoring hooks

### 7.2 Phase 2: Core Components (Week 2)

- [ ] Implement `RideCard3D` with 3D lift and tilt
- [ ] Create `MapContainer3D` wrapper for Leaflet map
- [ ] Develop `Input3D` with 3D focus states
- [ ] Build `Modal3D` container with depth
- [ ] Add haptic and sound feedback options

### 7.3 Phase 3: Integration & Refinement (Week 3)

- [ ] Replace buttons in OfferRidePage, FindRidePage, Dashboard
- [ ] Integrate ride cards in search results and inbox pages
- [ ] Apply 3D containers to dashboard widgets and forms
- [ ] Conduct performance testing on various devices
- [ ] Implement accessibility audits and fixes
- [ ] Add reduced motion preferences support

### 7.4 Phase 4: Polish & Documentation (Week 4)

- [ ] Create 3D UI storybook components
- [ ] Write usage guidelines for developers
- [ ] Add 3D UI section to existing PRD
- [ ] Create video demo of 3D interactions
- [ ] Gather feedback from usability testing
- [ ] Finalize and merge to main branch

---

## 8. Future Scope (Semester 7)

- **3D Map Exploration** - Experiment with Three.js for terrain-based campus map
- **Avatars & Presence** - Simple 3D avatars for user profiles
- **Gesture Controls** - Advanced touch gestures for 3D object manipulation
- **Environmental Effects** - Dynamic lighting based on time of day
- **Multiplayer 3D Space** - Shared virtual campus lobby for users to meet
- **AR Preview** - AR view of vehicle approaching pickup point using device camera

---

**Document Owner:** LiftLink Project Team — Parul University  
**Review Status:** Ready for developer feedback  
**Next Steps:** Share with frontend team for implementation planning  
