# Outfit (heading typeface) — origin and provenance

- **Family:** Outfit, by the Outfit Project Authors. **License:** SIL Open Font License 1.1 (`OFL.txt`, copied verbatim from upstream).
- **Official source:** <https://github.com/Outfitio/Outfit-Fonts>, file `fonts/variable/Outfit[wght].woff2` (45 064 bytes) and `OFL.txt`.
- **Downloaded:** 2026-11-10, with the maintainer's approval.
- **SHA-256 of the upstream file:** `d7340c446921781adfcf7c8fbffab32867904caa14cf6170533f5a58e2051e1b`
- **Shipped file:** `Outfit-latin-400-600.woff2` — 24 656 bytes (budget: 40 KB).
  SHA-256: `434adec93da78266a257dbd4d4076b8b19d6986c5950fb13e5917ca63c9823f1`

## How the shipped file was made (reproducible)

Weight axis limited to 400–600 and glyphs limited to Latin (Spanish and English text, typographic quotes, dashes, ellipsis, bullet, euro, minus).
No glyph was modified; the subset is derived work allowed by the OFL (the Reserved Font Name clause does not apply: the upstream license declares none).

```bash
pip install fonttools brotli          # in a throw-away virtualenv, not part of the project
fonttools varLib.instancer "Outfit[wght].woff2" wght=400:600 -o inst.woff2
pyftsubset inst.woff2 \
  --unicodes="U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201A,U+201C-201E,U+2022,U+2026,U+20AC,U+2212" \
  --layout-features="kern,liga,calt,ccmp,locl,mark,mkmk" --flavor=woff2 --output-file=Outfit-latin-400-600.woff2
```

Used only for `h1`–`h3`, highlighted figures and the product name (see ADR-0023). Body text keeps the system font.
