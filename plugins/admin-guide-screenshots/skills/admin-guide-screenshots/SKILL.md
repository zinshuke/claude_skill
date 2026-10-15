---
name: admin-guide-screenshots
description: Write step-by-step admin guides for a web admin panel (Joomla by default) where every step has a screenshot cropped to the field or section the step talks about, with a colored box, a numbered badge and a short note on it. Runs an intake questionnaire, reviews the feature's code into an inventory, gets the outline approved, then captures and writes section by section, resuming across sessions. Use when the user asks for an admin guide, user manual, how-to or tutorial with screenshots, to continue such a guide, or to (re)take its screenshots.
---

# Admin guide screenshots

A guide covers ONE feature (an extension, a module of the app, one admin area), never a whole project.
Each step = one instruction + one screenshot of the field/section the step is about: a colored box
(red by default), a badge with the step number and a short note saying what the box is (several
targets in one step: `2a`, `2b`, `2c` in the order the user acts on them). The image is cropped to the
boxes plus padding, so the reader sees the target and its surroundings, not the whole page.

Everything about a guide lives in `docs/admin-guide-screenshots/<guide>/` in the project:

| File | Holds |
|---|---|
| `guide.json` | Intake answers, doc link, sections with their status and shots, uploaded assets. The resume point. |
| `inventory.md` | The feature review: screens, actions, fields, permissions, states, public-site effects, gaps. |
| `shots.json` | The shot list `scripts/shoot.py` runs. |
| `img/*.png` | Captured screenshots. |
| `<guide>-admin-guide.md` | Local Markdown copy of the guide, images linked from `img/`. Always kept, even when the main output is a Claude Doc. |
| `index.html` | HTML page built from the Markdown copy (Phase 6). `docs/admin-guide-screenshots/index.html` lists all guides. |

**Where results go.** Guides are for people who never open hidden folders, so everything above lives in
the project's visible `docs/admin-guide-screenshots/` (named after this skill so it never clashes with the
project's own `docs/` folders). Never keep a guide only in a hidden or tool folder (`.claude/`, this
skill's or the plugin's folder, a temp or scratch folder). Found one there, or in the old
`docs/admin-guides/`? Move its folder to `docs/admin-guide-screenshots/<guide>/`, fix the paths in its
`guide.json` (`output_local`, `output.path`), rebuild the pages (Phase 6), and delete the old folder
once the new pages work. End every session by giving the user the path of the guide's `index.html`.

Credentials: `.claude/admin-guide.env` (`ADMIN_GUIDE_USER=` / `ADMIN_GUIDE_PASS=`, chmod 600), one per
project, outside the skill folder. Never in `guide.json`, a shot list, the skill folder or the guide.

`<skill>` in the commands below = this skill's base directory (the folder holding this SKILL.md:
`.claude/skills/admin-guide-screenshots` in a project, or the plugin's install folder). Commands run from
the project root.

## Phase 0: find or start the guide

1. List `docs/admin-guide-screenshots/*/guide.json`. Also check `docs/admin-guides/*/guide.json` and
   hidden folders, and move what you find there as described in "Where results go". If the request names a guide that exists ("continue the SiteKit
   guide"), load it, show a one-line status per section, skip answered intake questions, and go to the
   first section that is not `written`.
2. No guide yet and the feature is not named: discover candidates and ask which one.
   Joomla: `python3 <skill>/scripts/list_extensions.py` (third-party only;
   `--all` includes core). Other apps: list admin routes/menus/modules from the code.

## Phase 1: intake questions

Ask with AskUserQuestion, at most 4 questions per call, two rounds. Each question offers concrete options;
put the recommended one first. Skip any question already answered in `guide.json` or in the request.
Unanswered ones are stored as `null` and asked next time they matter.

Round 1: what to write
1. **Feature**: which extension/area (options from Phase 0 discovery).
2. **Audience**: site owner / non-technical admin (default) · shop or content staff · developer / integrator.
   Sets tone and depth (no code or file paths for non-technical readers).
3. **Guide type**: task-based setup walkthrough (default) · screen-by-screen reference · both.
4. **Output and language**: Claude Doc (default, shareable, comments) · Markdown file in the repo · both;
   and the guide's language.

Round 2: how to capture
5. **Site and login**: base URL (default from the project config, e.g. Docker port), and the role to
   capture as (Super User default; a limited role if the guide is for staff). Missing credentials → ask
   the user to put them in `.claude/admin-guide.env` themselves, or to give them so you write that file.
6. **Privacy**: what to blur: account emails · account/property IDs · API keys/secrets · nothing.
7. **Domain shown**: the local URL as-is, or note that the reader's URLs will differ (screenshots
   always show the real local URL; never fake it).
8. **Style**: box color (red `#e5262f` default, or the brand color), images cropped to the boxes with
   60 px padding (default) or full page, numbered badge + short note on each box, 1440×900 viewport.
   Store it in `answers.style` and set `color` / `crop` at the top of `shots.json` from it.

Write the answers to `guide.json` (`answers`) before going further.

## Phase 2: review the feature → `inventory.md`

Review the code, not memory. For each part, note file paths you read.
- Admin menu entries and every screen (views/layouts/templates).
- Per screen: toolbar buttons, forms and fields (labels exactly as shown, via the language files),
  tabs, filters, links to other screens, messages it can show.
- Actions/tasks (controllers), and what each changes.
- Permissions/ACL that gate screens or actions.
- States that change what screens show (not configured / connected / trial / error, empty vs data).
- Effects outside the admin (public-site output, emails, cron/CLI).
- Related extensions (plugins/modules) and their settings.
- Gaps: strings or tasks with no UI, dead links, inconsistent permissions. Report them to the user; the
  guide documents what exists, it does not invent UI.
If the live site is available, open the main screens once to confirm the inventory matches.

## Phase 3: outline → user approval

From the inventory and the intake answers, write the sections into `guide.json` (`sections`), task-based
by default ("Connect Google", "Set up Analytics", then reference/troubleshooting). Per section record:
`state_needed` (site state for its screenshots), `needs_user` (things only the user can do: external
logins, real payments, public URLs, external-console screenshots) and `status: "planned"`.

Show the outline as a short table (section · state needed · what the user must prepare) and **stop for
approval**. Order capture so "empty/before" states come first: they disappear once things get configured.

**Who sets up each state.** Mark each section `setup: "user"` or `setup: "claude"`:
- `user`: anything outside the site (Google/payment/email logins, external consoles, public DNS), real
  money, or real customer data.
- `claude`: states reachable inside the site's own admin: sample records (a test product, category,
  order, user), settings toggles, enabling a plugin. Most features with no third party are all `claude`.
  Ask once in the approval message, listing what will be created or changed (e.g. "create 1 test
  product 'Guide sample', switch X on"). Prefer doing it through the admin UI with the shot list's
  `actions` (that is also what the guide shows) rather than raw SQL. Use clearly named sample data
  ("Guide sample …"), record every created record and changed setting with its previous value in
  `guide.json.changes`, and after the section is captured offer to revert them. Never delete or edit
  existing real records to get a screenshot.

## Phase 4: create or reuse the doc

Claude Doc: if `guide.json.doc.url` exists, reuse it (read it first; never recreate). Otherwise create the
doc with one pending block per approved section (follow the docs connector's instructions), then store
`doc.url`, `doc.id` and `doc.body_node` in `guide.json`. Markdown only: `docs/admin-guide-screenshots/<guide>/<guide>-admin-guide.md` unless
the user chose another path; store it in `guide.json.output.path`.

## Phase 5: per section: capture → check → write

Work one section at a time. Before capturing, confirm the site is in the section's `state_needed`;
if it needs the user, say exactly what to do and wait.

1. Add the section's shots to `shots.json`:
   ```json
   {"name": "byo-02-credentials",
    "url": "/administrator/index.php?option=com_x&view=settings",
    "actions": [{"fill": ["#client_id", "123-example.apps.googleusercontent.com"]}],
    "highlights": [{"selector": ".mb-3:has(#client_id)", "label": "2a", "note": "Paste the Client ID"},
                   {"selector": "#adminForm button[type=submit]", "label": "2b", "note": "Save"}]}
   ```
   - `"note"` on every highlight: 2 to 8 words in the guide's language saying what the box is or what to
     do there ("Paste the Client ID", "Shows the connection status"). It is drawn next to the badge.
   - `"color"`: any CSS color, at the top of `shots.json` for the whole guide (default `#e5262f`), on a
     shot, or on one highlight (e.g. green for "result", red for "action"). The badge text switches to
     black on light colors.
   - Cropping: by default each image is cropped to its boxes and notes plus padding, at least 800×400.
     Tune it with `"crop": {"padding": 60, "min_width": 800, "min_height": 400}` at the top or on a shot;
     `"crop": false` keeps the whole page (overview shots of a screen). `"crop_include": [selectors]`
     widens the crop to other things the reader must see (an open dropdown, the message after save).
     Several boxes far apart give a big crop: split them into separate shots instead.
   - `"badge": "right"`, `"top"` or `"bottom"` on a highlight moves its badge and note when the default
     (left) would cover something; when a spot has no room the next one is used.
   - `"post_actions"`: actions run after the boxes are drawn, for menus that close when the page scrolls
     (box the button, then open its menu). `"full_page": false` for pop-up dialogs (viewport only).
   - `"settle_ms"` (default 300) waits before and after drawing boxes; use ~2500 on pages with charts so they finish animating.
   - Selectors: the wrapper holding label + input + help (`.mb-3:has(#id)`, `.card:has(h2)`), found by
     reading the template, not guessed.
   - `actions`: `click`, `fill`, `select`, `hover`, `wait` (selector), `wait_ms`, `eval` (JS). Never submit
     a form that saves real settings unless the user asked; example values in unsaved fields are fine.
   - Shots that save are not repeatable: run the one that creates a record once, then make its "saved"
     shot open the existing record and save it unchanged (same success message, no duplicates).
     Joomla success/error messages: `#system-message-container joomla-alert`. Joomla edit screens
     remember the last open tab: click the tab a shot needs instead of assuming the first one.
   - `blur` (from the privacy answer) and `hide` (debug bars, cookie banners), global or per shot.
2. Run from the project root:
   ```bash
   python3 <skill>/scripts/shoot.py docs/admin-guide-screenshots/<guide>/shots.json \
       --out docs/admin-guide-screenshots/<guide>/img --only <shot names>
   ```
   `WARN … selector not found` = fix the selector, retake with `--only`.
3. Look at every PNG (Read tool): box on the right element, badge and note readable and not covering
   another box, crop showing enough to find the spot on the screen, blurred items blurred, no
   debug output or PHP notices. Retake until right.
4. Publish: Claude Doc → upload the PNGs as assets to the doc's URL, create a blob per asset, embed
   `![Step N: …](blob/<id>)` under its step (docs connector `topic.uploads`); store asset and blob ids in
   `guide.json.assets` so retakes replace the right image. Markdown → `![Step N: …](img/<name>.png)` with
   the images copied next to the file.
5. Write the section (replace its pending block) and set its status to `written` (or `partial` with a
   note of what is missing) in `guide.json`. Record screenshots that still need a state in the
   section's `missing` list.
6. Update the local copy `docs/admin-guide-screenshots/<guide>/<guide>-admin-guide.md` with the same section,
   images as `img/<name>.png`. Write it yourself: the docs export replaces images with placeholders.
   If the doc was edited by someone else, read it first and bring their changes into the copy.

## Phase 6: build the HTML pages

After a session that wrote or changed sections (and always when a guide is finished), rebuild:

```bash
python3 <skill>/scripts/build_html.py            # all guides + index
python3 <skill>/scripts/build_html.py --guide <guide>
python3 <skill>/scripts/build_html.py --guide <guide> --embed   # one self-contained file
python3 <skill>/scripts/build_html.py --zip       # + docs/admin-guide-screenshots-html-<date>.zip
```

- Output: `docs/admin-guide-screenshots/<guide>/index.html` (screenshots linked from `img/`) and
  `docs/admin-guide-screenshots/index.html` (a card per guide). Title, audience, language and the online link
  come from `guide.json`; the content comes from `<guide>-admin-guide.md`, so update that first.
- The page has a contents sidebar with search, numbered step markers, captions from the alt text,
  click-to-zoom screenshots, light/dark mode and a print/PDF layout. Step markers take the `color` of
  the guide's `shots.json`, so they match the badges in the screenshots.
- `--zip [FILE]` packs the index, the guide pages and only the screenshots they use (no guide.json,
  shots.json, inventory or Markdown) into one zip that unzips to an `admin-guide-screenshots/` folder; combine
  with `--guide` for one guide. Use it when the user wants to send or host the guides. Unzip it once
  to a temporary folder and check every image link resolves before handing it over.
- `--embed` inlines the screenshots (a few MB) so the page can be emailed or attached; rebuild without
  it afterwards to keep the folder light.
- Check one page in a browser after building (desktop and ~390 px wide): steps numbered, images
  showing, no sideways scrolling. Needs `pip install markdown`.

## Writing rules

- Numbered steps. Each starts with the action and names UI labels in bold exactly as on screen
  ("Click **Save & Close**"); its number matches the badge.
- Image right under its step; alt text "Step N: <what it shows>".
- The step text and the box notes agree: a note is the short form of what the step says about that box.
- Prerequisites (permission, state) once at the top of the section.
- Steps outside the site (Google Cloud Console, email) are named as such; their screenshots come from
  the user.
- Tone and depth follow the audience answer; the language follows the language answer.

## Other projects and apps

Install it as a plugin, copy this folder into another project's `.claude/skills/`, or move it to
`~/.claude/skills/` for all projects. Per project: `.claude/admin-guide.env` and `docs/admin-guide-screenshots/`. For a non-Joomla admin, add
the login form to `shots.json`:
`"login": {"url": "/admin/login", "user": "#email", "pass": "#password", "submit": "button[type=submit]", "done": "nav"}`.
Needs Python 3 + `pip install playwright`; uses Playwright's Chromium, or installed Google Chrome as fallback.
