# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Played both solo and multiplayer, and both are first-class. Solo: one player against computer opponents (five difficulty levels), casual or ranked, with no network needed in the desktop app. Multiplayer: friends play together online, where one person hosts a room and the others join from a phone browser or the desktop app. Players already know Sanguosha (三國殺) rules and its terminology; the interface assumes that knowledge. Phone and desktop matter equally.

## Product Purpose
「進化三國」is a homebrew Sanguosha simulator with its own heroes, skills and rules. It runs the full rules engine, computer opponents of five difficulty levels, multiplayer rooms, a ranked ladder with points and ranks, and several game modes (identity modes, 暗殺目標, 抓叛徒, 雙國戰, 2-3 player modes). Success is a table where a player always knows whose turn it is, what a card or skill does, and what to tap next, without reading the rules.

## Positioning
A Sanguosha game whose hero roster and rules are the author's own, with an engine that explains itself (skill text, battle log, tutorial) in Traditional Chinese, English and Japanese.

## Operating Context
- Delivered as a Python server serving a single-page web client (`web/index.html`, `anim.js`, theme and i18n scripts), deployed at a public HTTPS address, and also packaged as a Windows Electron app that bundles the server.
- Play is turn-based with timers and animated card movement over a seat layout of 2 to 10 players; the player's own hand is at the bottom.
- Accounts, friends, rooms, spectating and rank profiles exist server-side.

## Capabilities and Constraints
- Three UI languages (zh, en, ja); every visible string has to work in all three.
- A theme system remaps colors; role and team colors must survive it.
- Seat frames, role badges, tags (such as the flipped-over tag) and animations overlay the same table; z-order and scrolling behaviour on phones are known sensitive areas.
- Any change is tested locally first and only pushed to production after the owner approves.
- Purchasable cosmetics (avatar effects, avatar frames, play animations) are keyed by id and owned per account; redesigns must keep ids so existing ownership still works.
- Owner judgment, to be re-checked by looking at the rendered result: the play animations 墨韻丹青, 驚雷破空, 赤壁烈焰 and 武士, and the avatar effects that only float a few particles, are not good enough and lack originality.
- Asset production: the owner can generate images locally with ComfyUI and SDXL. Historical accuracy comes from line-art or reference images supplied to ControlNet and IP-Adapter, not from text prompts alone. Reference images should be public-domain.

## Brand Commitments
Name「進化三國」. Traditional Chinese is the primary language. Existing hero names, skill text and the card art style stay as they are, with one confirmed exception: weapon and armor card art does not match the historical objects they are named after and may be redrawn to match history (owner confirmed). Basic cards, tricks and horses keep their current art.

## Evidence on Hand
Hero and skill text in `characters.md`, translations in `web/i18n*.js`, screenshots in `shots/`. No testimonials, player counts or external references have been provided; none should be invented.

## Product Principles
1. The state of the game is readable at a glance: turn, targets, tags, HP.
2. Rules explain themselves in the interface instead of requiring outside knowledge.
3. Phone and desktop get the same game, not a reduced one.
4. Animation conveys what happened; it never blocks or hides the next decision.
5. Existing players' habits and the established look are preserved unless a change is clearly better.
