# Joomla Articles admin inventory

Reviewed 2026-10-15 from `administrator/components/com_content` (Joomla 6.1.4 core): `src/View/Articles/HtmlView.php`,
`src/View/Article/HtmlView.php`, `tmpl/articles/{default,emptystate,default_batch_body}.php`, `tmpl/article/edit.php`,
`forms/{article,filter_articles}.xml`, and the live admin at http://localhost:3000.

## Site state at review
- 0 articles; 1 category (`Uncategorised`, published). Articles list shows the empty state.
- com_content options: workflows off (`workflow_enabled=0`), version history on (`save_history=1`, 10 versions),
  Images and Links tab shown (`show_urls_images_backend=1`), Publishing and Options tabs shown.
- Editor: TinyMCE (default), CodeMirror and None available. Content plugins: Fields, Page Break, Smart Search on; Vote off.

## Menu
Content → Articles (+ quick add), Categories (+), Fields, Field Groups, Media, Site Modules, Administrator Modules.
Featured Articles is a separate list (Content → Featured Articles where enabled in the menu).

## Articles list (`view=articles`)
- Empty state: "No Articles have been created yet." with **Add your first article** and **Learn More**.
- Toolbar: **New**; **Actions** dropdown (needs a selected row): Publish, Unpublish, Feature, Unfeature, Archive,
  Check-in, Trash, Batch; **Delete** (only when the status filter is Trashed); **Options**; **Help**.
  With workflows on, Actions shows workflow transitions instead (not the case here).
- Search tools: search box (title, `id:`, `author:`, `content:` prefixes), Filter Options (status, featured, category,
  access, author, language, tag, max levels), sort and list limit. Columns to be confirmed once articles exist.
- Batch: set language, access, category (move/copy), tags.

## Article edit (`task=article.add` / `article.edit`)
- Toolbar: **Save**, **Save & Close** (dropdown: Save & New, Save as Copy), **Cancel** (Close after the first save),
  **Toggle Inline Help**, **Help**. Versions, Preview and Accessibility Check appear for saved articles (to confirm).
- Top: **Title** \*, **Alias** ("Auto-generate from title").
- Tabs: **Content** (Article Text editor + Toggle Editor; right column Status, Category \*, Featured, Access, Tags,
  Note, Version Note), **Images and Links** (Intro Image, Full Article Image, links A/B/C), **Options** (layout and
  show/hide overrides), **Schema** (structured data), **Publishing** (Start Publishing, Finish Publishing,
  Created Date, Created By, Created by Alias, Modified Date/By, Revision, Hits, ID; Metadata: Meta Description
  (300 chars), Keywords, Robots, Author, Content Rights), **Configure Edit Screen**, **Permissions**.
  Associations tab only on multilingual sites.

## Permissions (core groups)
Author: create, edit own. Editor: + edit any. Publisher: + publish/unpublish. Manager/Administrator/Super Users:
everything. Set per site in Articles → Options → Permissions, per category, or per article (Permissions tab).

## Public site
An article shows when: status Published, inside its Start/Finish Publishing dates, its category is published,
the visitor's access level allows it, and a menu item / category / featured list links to it.

## Gaps / notes
- Schema tab is new in Joomla 5+; it is a reference area outside everyday tasks.
