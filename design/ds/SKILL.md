---
name: crosscheck-design
description: Use this skill to generate well-branded interfaces and assets for Crosscheck, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.
If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.
If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Crosscheck-specific rules that override defaults: system font stack only (no web fonts, no icon font), weights 400 and 600 only, every figure in monospace with a source line beneath it, chromatic colour only for the four verdicts (glyph + word + colour, never colour alone), no shadows or gradients, phone-first one column at 360px with a 640px max content width, sentence case, no emoji, no exclamation marks, no deficit language. The full rulebook is `design/DESIGN.md`; tokens are `design/tokens.json` and `design/tokens/*.css`.
