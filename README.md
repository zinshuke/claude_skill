# claude_skill

A Claude Code plugin marketplace.

## Plugins

### admin-guide-screenshots

Writes step-by-step admin guides for a web admin panel (Joomla by default). Every step has a full-page
screenshot with a red box and a numbered badge on the field or section the step describes.

How it works:
- asks intake questions (feature, audience, guide type, output, language, login, privacy)
- reviews the feature's code into an inventory, then gets your approval on an outline
- captures and writes one section at a time, and can resume across sessions
- publishes as a Claude Doc and/or Markdown, and builds HTML pages (search, zoom, dark mode, print)

## Install

In Claude Code:

```
/plugin marketplace add zinshuke/claude_skill
/plugin install admin-guide-screenshots@claude-skill
```

Or copy `plugins/admin-guide-screenshots/skills/admin-guide-screenshots/` into a project's
`.claude/skills/` (one project) or `~/.claude/skills/` (all projects).

## Requirements

```bash
pip install playwright markdown
python3 -m playwright install chromium   # or use an installed Google Chrome
```

## Per-project setup

- Admin login: `.claude/admin-guide.env` in the project (keep it out of git, `chmod 600`):
  ```
  ADMIN_GUIDE_USER=admin
  ADMIN_GUIDE_PASS=...
  ```
- Guides are written to `docs/admin-guides/<guide>/`.
- Joomla's administrator login form is the default. For any other admin panel, add a `login` block to
  `shots.json`:
  ```json
  "login": {"url": "/admin/login", "user": "#email", "pass": "#password", "submit": "button[type=submit]", "done": "nav"}
  ```

See `shots.example.json` in the skill folder for the shot-list format.
