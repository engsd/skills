# Kami Reading Style

Use this style for long prose that should feel like a carefully typeset paper
document: essays, articles, DOCX memos, letters, one-pagers, reports,
manuscripts, changelogs, portfolios, and readable long-form Markdown.

Underlying System: Kami Parchment Document

Primary reference: `prompts/styles/references/kami-reading/doc-kami-parchment.html`.
This replaces the older Kami longform treatment. Keep the `kami-reading` style
id for compatibility, but visually follow the new `doc-kami-parchment`
reference.

Treat the reference as a structural and visual contract, not a file to copy
blindly. The generated artifact must still be a polished html-anything page:
single-file where practical, responsive, accessible, offline-friendly except
for explicitly allowed source images/fonts, and verified in a browser.

## First Viewport Contract

The first viewport must immediately read as a composed printed document:

1. Warm parchment canvas, never pure white.
2. Thin editorial masthead or logotype row with metadata.
3. Large serif title, restrained lede, and one ink-blue accent or tag.
4. Hairline rules that frame the reading surface without card-heavy chrome.
5. One to three quiet document-native content blocks: pillars, lede notes,
   key claims, or a compact table of contents.
6. No dashboard grid, marketing hero, app top bar, sticky side rail, neon,
   gradients, glass, or heavy shadows.

## Visual Signature

Use these tokens or very close equivalents:

```css
--paper: #f5f4ed;
--paper-2: #efeee5;
--ink: #1f1d18;
--muted: #6b665b;
--rule: #d4d1c5;
--accent: #1B365D;
```

Rules:

- The background is warm parchment `#f5f4ed`.
- The only chromatic accent is ink blue `#1B365D`.
- Use warm grays only; avoid cool gray and blue-gray surfaces.
- Prefer 1px hairline rules and solid borders over shadows.
- Avoid drop shadows, blur, neon, gradients, and decorative blobs.
- Border radius should be small and print-like; avoid rounded app cards.
- Tags use solid hex fills or hairline outlines, never translucent rgba
  effects.
- Do not depend on Tailwind CDN even if the reference does. Inline the needed
  CSS in the final HTML.

## Typography

- Use one serif family for the document voice.
- English stack: `Charter, "Source Serif Pro", "Iowan Old Style", Georgia, serif`.
- Chinese stack: `"TsangerJinKai02 W04", "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif`.
- Body weight 400; heading weight 500 or 600 only when necessary.
- Do not synthesize heavy 800/900 display weights.
- Reading body line-height: 1.5 to 1.55.
- Compact notes: 1.4 to 1.45.
- Headings: 1.1 to 1.3.
- Article width should feel like 62 to 72 characters per line.

The imported reference contains italic details. For new output, use italics
sparingly and only when typographically justified; do not make italic quotes a
core style feature.

## Layout Variants

Choose the document shape from the source:

- **One-Pager**: masthead, title, lede, three editorial pillars, footer
  metadata.
- **Long Doc**: cover, inline contents, section pages, notes, colophon.
- **Letter**: address block, date, recipient, body, signature line.
- **Portfolio**: project title, one visual bay, role/time/stack metadata,
  project narrative.
- **Resume**: name, tagline, contact row, experience, skills, education.
- **Report**: title, thesis, key metrics row, body analysis, compact mono/SVG
  chart if needed.
- **Changelog**: version, date, Added/Changed/Fixed sections.

## Component Vocabulary

Use at least four of these primitives, with class names preserved when useful:

- `.kami-reader`
- `.kami-masthead`
- `.kami-cover`
- `.kami-title`
- `.kami-lede`
- `.kami-rule`
- `.kami-tag`
- `.kami-toc`
- `.kami-page`
- `.kami-pillar`
- `.kami-note`
- `.kami-progress`
- `.kami-colophon`

## Interaction Model

Keep interactions small and document-native:

- Reading progress indicator.
- Inline contents navigation.
- Collapsible notes/source appendix.
- Optional tiny print/copy controls.

Do not make it an app shell. Long prose should privilege reading, navigation,
annotation, and source inspection.

## Content Treatment

- Preserve the author's hierarchy and sequence.
- Convert long paragraphs into comfortable reading blocks.
- Pull out a small number of key claims as quiet notes or pillars.
- Keep caveats and source metadata visible.
- Use tables only when they clarify the document.
- Use source images as document figures when available; otherwise do not add
  decorative placeholder art.

## Avoid

- The older generic Kami shell if it does not resemble
  `doc-kami-parchment.html`.
- Dashboard-first pages.
- Generic blog templates.
- Marketing hero sections.
- Sticky sidebars and heavy toolbars.
- Multi-color palettes.
- Pure white canvas.
- Cool grays.
- Heavy bold serif.
- Floating piles of cards.
- Unsupported conclusions.

## Final Style Gate

Before finalizing, verify:

- The root html declares `data-ha-style="kami-reading"`.
- The page would still look like a `doc-kami-parchment` page if all content
  were replaced.
- The first viewport has the parchment, masthead, serif title, lede, ink-blue
  restraint, and hairline-rule geometry from the reference.
- The final HTML does not rely on Tailwind CDN from the reference.
- Text is readable on mobile and desktop with no horizontal overflow.
