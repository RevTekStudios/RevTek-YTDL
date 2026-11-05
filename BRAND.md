# RevTek Studios — RTS Abyss

The selected direction is **29 — Abyss Blue** with the **refined Folded Form R** (third in the four-logo refinement round, originally concept 05). This replaces the initial mint concept. This is the RTS brand standard, now applied to RevTek Link2Audio.

## Foundation

| Role | Hex | Use |
|---|---|---|
| Background | `#040A12` | Main canvas; selected base |
| Surface | `#0C1723` | Cards and grouped controls |
| Raised surface | `#142333` | Menus, dialogs, secondary buttons |
| Hover surface | `#1C3043` | Neutral hovered items |
| Subtle border | `#243B50` | Decorative separators only |
| Control border | `#58748C` | Recognizable input boundaries |
| Primary text | `#E7EFF5` | Selected text color |
| Secondary text | `#A9BECE` | Supporting content |
| Muted text | `#849DB1` | Metadata |
| Abyss identity | `#437798` | Selected logo color |
| Deep Abyss | `#315F83` | Selected supporting blue |

Keep Abyss Blue as the identity color. It is deliberately restrained: use it for substantial emblems and supporting fills, not small text or the only indicator of an interactive control. On light backgrounds, use a solid dark-ink logo.

## Highlights

| Family | Highlight | Tinted background | Default meaning |
|---|---|---|---|
| Ion cyan | `#50CFFF` | `#0B2B3A` | Primary action, focus, selection |
| Signal blue | `#6BA8FF` | `#10263F` | Information and progress |
| Silver | `#C9D7E2` | `#142333` | Neutral emphasis |
| Solar amber | `#F5B95F` | `#352719` | Warning and attention |
| Nebula violet | `#B49AFF` | `#271E3B` | Optional creative feature/category |
| Aurora mint | `#69D6AE` | `#112F29` | Success and completion |
| Flare rose | `#FF8FA8` | `#391E2A` | Error and destructive actions |
| Copper coral | `#F59A78` | `#37241F` | Optional chart/category color |

**Default signature: Abyss + silver + Ion cyan.** Amber adds strong warm contrast when attention is needed. Violet provides a distinct optional accent. Success, warning, and error keep the same meanings across all RTS programs.

Keep large areas neutral. As a flexible visual balance, aim around 85% dark foundation, 10% text/steel-blue identity, and 5% bright highlights. Use at most one optional category accent per screen. The full scale is a vocabulary, not a requirement to display every color.

## Component rules

- Primary button: Ion `#50CFFF` with ink `#040A12` label. Hover `#7EE0FF`; pressed `#289ABD`.
- Secondary button: raised surface, primary text, visible control border. Hover uses the neutral hover surface.
- Selection: Ion tinted background, pale Ion `#B2EEFF` text, cyan indicator, plus check or selected label where needed.
- Links: Signal `#93BEFF`, with underline or another persistent link cue.
- Keyboard focus: Ion cyan, 2 px outline and 2 px offset; distinguish it from hover.
- Status banner: dark family tint, bright family text, explicit status label or icon.
- Disabled: raised surface and muted text, no hover change, disabled interaction. Avoid variable opacity.
- Bright filled buttons use dark ink labels. Dark tinted banners use bright family text. Avoid white on bright highlight fills.
- Status and chart colors always have a second cue: text, symbols, shapes, or line styles.

## Shared scales and files

Nine families have seven levels: 100, 200, 300, 400, 500, 600, 900, progressing from pale to dark. Level 400 is the standard highlight and 900 is a dark tinted background; Abyss and Silver are identity/neutral ramps.

- [Portable tokens](design/rts-tokens.json): reusable by desktop and web clients.
- [CSS variables](design/rts-tokens.css): generated web tokens.
- [Generator](design/rts-color-system.py): generates tokens and calculates contrast.
- [Contrast report](design/contrast.md): all 27 specified pairings meet their 4.5:1 text or 3:1 control targets. Other combinations need their own checks; subtle separators are decorative only.

Use semantic names across apps instead of scattering hex values through components. Products can vary layout and one secondary category accent while retaining the studio mark, foundation, primary interaction color, and status meanings. Use Segoe UI on Windows, system sans-serif elsewhere, clear hierarchy, restrained uppercase labels, generous spacing, and visible keyboard focus.

## Scope and exceptions

RTS Abyss is the default for new RevTek applications. **Officer Assist and all its variants are explicitly exempt**: preserve their established identity and existing themes. Older products such as SystemForge may be migrated later, as separate work; this change only applies to this app.

## Logo assets

The folded R is reconstructed as flat vector geometry in `brand.py`. The same paths generate `assets/rts-mark.svg`, `assets/rts-logo.svg`, the transparent PNGs, and the Windows icon. Tk uses the same geometry for the header. All logo parts use one solid Abyss identity color. The PNG master is 1024 px; the SVG is scalable. The runtime loads the shared design tokens and the executable bundles them. The product name is **RevTek Link2Audio**, with Link2Audio used as the short interface title.

The selected Link2Audio product icon is **07 — Audio Reel**: a solid silver reel with three open slots and a cyan waveform, on an Abyss tile. It is deliberately distinct from the parent studio folded R, which stays in the app header. `assets/link2audio-icon.svg` and the 1024 px PNG are the product masters; `assets/app-icon.png` and `assets/app.ico` are generated runtime exports. All use solid fills.
