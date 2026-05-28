# Document Style

Use this style for **document-shaped** content: essays, articles, reading
lists, bookmarks, research collections, PDFs, DOCX, academic papers, legal
records, medical/lab records, policy documents, and other long or
high-stakes documents.

The style has two tones, picked from the source:

- **Narrative** (essays, articles, bookmarks, reading lists) — feels
  edited, sequenced, typographically intentional. Magazine-like.
- **Formal** (PDFs, DOCX, legal, medical, lab, policy) — feels like a
  structured dossier with evidence, caveats, and traceability.

The structural scaffold is identical in both tones. Only voice, density,
and color palette shift.

## Integrated Reference Variants

For document-shaped work, load and adapt these references when they match the
source. They are style references, not files to copy verbatim:

- `prompts/styles/references/document/article-magazine.html` for essays,
  articles, newsletters, public-facing research writeups, and polished
  narrative reports. Use its single-column editorial rhythm, masthead,
  large serif headline, metadata row, pull quote, ornaments, and end CTA.
- `prompts/styles/references/document/docs-page.html` for technical guides,
  process documentation, API/tutorial pages, runbooks, and knowledge-base
  entries. Use its three-column documentation scaffold: sticky left nav,
  central article, right on-page TOC, code blocks, callouts, and compact
  topbar.
- `prompts/styles/references/kami-reading/doc-kami-parchment.html` for calm
  paper-like one-pagers or long reading surfaces. Prefer routing explicit
  "kami", "paper reader", "easy to read", or manuscript requests to
  `kami-reading`, but borrow this reference when the document style needs a
  print-like parchment one-pager.

When using `article-magazine` or `docs-page`, keep the root style id as
`document` unless the user explicitly asked for `kami-reading`. Preserve the
reference scaffold and component vocabulary while translating the user's
content into it.

## Underlying System: Document Review

This is a reading and review system. The page is a structured document
with claims, evidence, and traceable detail — not a marketing page.

Base scaffold:

1. **Cover / masthead** — title, scope, source context, neutral summary
   or thesis deck, caveat if high-stakes.
2. **Reader rail** — section nav, reading modes (quick summary / outline
   / evidence), topic filters, or collection tabs.
3. **Body sheet** — sections or claims arranged as a memo, with clear
   hierarchy. Pull quotes for narrative tone; fact tables and definition
   lists for formal tone.
4. **Evidence spread** — excerpts, source labels, dates, parties, ranges,
   or row references. Clusters/topic cards for collection inputs.
5. **Drill-down / questions panel** — searchable source browser, plus
   "what to ask a clinician/attorney/accountant" or "what to read next"
   when relevant.

Component vocabulary:

- `.document-shell`, `.cover`, `.deck`, `.reader-rail`, `.body-section`,
  `.pull-quote`, `.claim-card`, `.fact-table`, `.evidence-margin`,
  `.caveat-box`, `.question-panel`, `.source-spread`,
  `.evidence-browser`.
- For article-magazine variants, also use `.article`, `.serif`,
  `.ornament`, `.pull-quote`, `.end-card`, `.byline`, `.article-meta`.
- For docs-page variants, also use `.topbar`, `.layout`, `.sidebar`,
  `.content`, `.toc`, `.callout`, `.codeblock`, `.pager`.
- Lean on typography, rules, columns, and quote treatment more than KPI
  cards. For formal documents, use tables and definition lists for
  extracted facts.

Interaction model:

- Reading modes change density or section visibility (5-minute summary /
  full outline / evidence-only).
- Topic/source filters support exploration but do not replace the
  narrative sequence.
- Claims link to evidence snippets. Search highlights evidence and
  headings.
- Do not gamify or overdramatize sensitive documents.

## Page Shape

- Lead with the sharpest thesis, executive summary, or reading path.
- Use a magazine-like section rhythm for narrative tone; a memo-like
  rhythm for formal tone.
- Preserve source nuance with short quoted excerpts. Quote sparingly and
  cite local evidence labels.
- Offer reading modes when helpful: 5-minute summary, full outline,
  evidence browser.
- For high-stakes records, include scope/caveat and an "ask a
  professional" checklist instead of recommendations.

## Visual Language

- Use the Clockless tokens from `prompts/styles/_design.md`.
- Strong typography, clear rules, disciplined whitespace.
- Visual density is deliberate: broadsheet for many items, spacious
  essay mode for one long piece, quiet review surface for formal
  documents.
- Use semantic muted color for formal tone; let images or generated art
  support the subject in narrative tone (never decorate).

## Required Modules

- TL;DR, thesis, or neutral executive summary.
- Scope / caveat note for formal documents.
- Section navigation.
- Key claims, themes, or extracted facts.
- Pull quotes / evidence snippets with source labels.
- Related topics, clusters, or definition cards.
- Source drill-down.
- For formal: questions / next review checklist.

## Avoid

- A generic blog template or dashboard layout.
- Treating every paragraph equally.
- Over-quoting source material.
- Decorative card stacks with no editorial hierarchy.
- Diagnosis, legal advice, accounting/tax advice, or definitive
  interpretation beyond what the document supports.
- Sensational language.
- Unsupported conclusions.

## Implementation Notes

- Respect copyright limits for quoted material; prefer concise paraphrase
  plus short citations/excerpts.
- For lab results, compare only against the reference range printed in
  the row.
- For legal/medical content, stay observational and recommend
  professional review for decisions.
- Keep links and source labels visible when the page is URL/research
  based.
