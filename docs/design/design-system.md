# MindWeave AI — Design System & Visual Identity

## 1. Visual Identity & Brand Palette

| Token Name | Hex Code | HSL / CSS Variable | Purpose |
|---|---|---|---|
| **Navy** | `#172B4D` | `brand-navy` | Root node, primary headers, high-contrast titles |
| **Blue** | `#3978D5` | `hsl(var(--primary))` / `brand-blue` | Main branches, active buttons, primary highlights |
| **Purple** | `#805AD5` | `hsl(var(--secondary))` / `brand-purple` | Sub-branches, AI sparkle accents, badges |
| **Canvas** | `#F4F6FA` | `hsl(var(--background))` / `brand-canvas` | Global application canvas & workspace background |
| **Surface** | `#FFFFFF` | `hsl(var(--card))` | Rounded cards, modal dialogs, knowledge panels |
| **Border** | `#E2E8F0` | `hsl(var(--border))` | Subtle dividers and card containers |

## 2. Mindmap Node Topology & State Colors

| Node Type / State | Color Token | Visual Presentation |
|---|---|---|
| **Root Node (Depth 0)** | `#172B4D` (Navy) | Solid navy background, white text, bold font |
| **Main Branch (Depth 1)** | `#3978D5` (Blue) | Soft blue tinted background, blue border, deep text |
| **Sub-Branch (Depth 2+)** | `#805AD5` (Purple) | Soft purple tinted background, purple border |
| **Selected Node** | `#3978D5` (Ring) | `ring-2 ring-primary ring-offset-2`, elevated shadow |
| **Generating Node** | `#F59E0B` (Amber) | Amber status badge, pulsing animation (`animate-pulse`) |
| **Failed Node** | `#EF4444` (Red) | Red error border, retry indicator tag |

## 3. Typography Hierarchy

- **Font Family:** `Inter`, -apple-system, sans-serif.
- **Code & Tech:** `JetBrains Mono`, monospace.
- **Heading 1:** 28px–32px, `font-bold`, `tracking-tight`, Navy (`#172B4D`).
- **Heading 2:** 20px–24px, `font-semibold`, Navy (`#172B4D`).
- **Heading 3:** 16px–18px, `font-medium`, Slate 800.
- **Body & Prose:** 14px–15px, `leading-relaxed` (1.625), max-width 65ch (`max-w-prose`) for comfortable reading.
- **Captions & Metadata:** 12px, Slate 500.

## 4. Component Rules

- **Cards:** `rounded-xl` (12px), background `#FFFFFF`, border `#E2E8F0`, subtle shadow.
- **Buttons:** Height 36px–40px, `rounded-lg`, smooth hover transition (`transition-colors duration-150`).
- **Contrast:** Every text color strictly satisfies WCAG AA (>= 4.5:1 ratio).
- **Animations:** Subtle and purposeful (`duration-150` to `duration-200`). No disorienting layout shifts.
