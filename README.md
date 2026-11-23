# One Day, One World — Monday 23 November 2026

[![make.fun bounty: news-image-20261123](https://img.shields.io/badge/make.fun-news--image--20261123-blue)](https://make.fun/bounty/news-image-20261123)
[![news-image-20261123 pot: $100](https://img.shields.io/badge/news--image--20261123-pot--%24100-green)](https://make.fun/bounty/news-image-20261123)
[![news-image-20261123 deadline: 25 Nov 2026](https://img.shields.io/badge/news--image--20261123-deadline--25--Nov--2026-orange)](https://make.fun/bounty/news-image-20261123)

A program that draws a newspaper front page summing up **23 November 2026's
world news in one image** — an entry for the make.fun bounty
[`news-image-20261123`](https://make.fun/bounty/news-image-20261123)
("Sum up 23 November's world news in one image", $100 pot).

## The image

A hero-led broadsheet front page, **"THE WORLD IN ONE PAGE"**, dated
**MONDAY 23 NOVEMBER 2026** in a red dateline bar. The distinctive centrepiece
is a hand-drawn, map-style illustration of the **Strait of Hormuz** — Iran
above, Oman and the U.A.E. below, tankers on a dashed shipping lane, a compass
rose, and an alert burst marking where the tankers were hit.

Stories covered (all reported 23 November 2026):

- **Hero — HORMUZ ON EDGE / TRUMP: NEW STRIKES AFTER JAN 1.** Two oil
  tankers hit by projectiles in the Strait of Hormuz; Iran says it downed
  two US drones and struck Patriot radars in Bahrain; Trump warns of fresh
  US strikes after 1 January if no deal is reached.
- **COP31 COLLAPSES.** The Antalya climate talks end with no deal after
  record overtime; the EU rejects a pact that never even names fossil fuels.
- **INDIA 720/9 IN WELLINGTON.** Pant (128) and Rahul (136) power a record
  Test total; New Zealand 119/2 at stumps.
- **MODI MEETS NEPAL'S SHAH.** Nepal PM Balendra Shah holds talks in Delhi
  on energy, hydropower and rail.
- **BANTEN FACTORY FIRE.** 24 body bags found at the Banten candy factory;
  dozens of workers still missing.
- **Also today:** Mexico captures FBI-wanted "El Chapo Isidro"; UN talks on
  lethal AI weapons continue; a Russian cargo ship burns off Finland;
  14 missing after a drone hit near Kyiv.

## Run it

Pure Python 3 standard library — no third-party packages, no network, no
external files. Text is rendered with an embedded 5x7 bitmap font and the
PNG is encoded by hand (zlib).

```sh
python3 main.py   # writes /output/entry.png (1024x1024, ~20 KB)
```

Two runs produce byte-identical output (verified: same SHA-256).

## Files

- `main.py` — the whole program: canvas, bitmap font, PNG writer, the
  Hormuz illustration, and the front-page layout.
- `README.md` — this file.
- `LICENSE` — MIT.

## Note on the kit

The official kit (`https://make.fun/c/news-image-20261123/kit`) returned
HTTP 503 "kit being built" on every attempt for 30+ minutes while this entry
was built, so the kit's README template could not be read. This README and
the entrypoint follow the bounty requirements as published
(`main.py` writing one 1024x1024 PNG to `/output/entry.png`); please check
the README badges against the kit template before submitting.
