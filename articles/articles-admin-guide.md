# Joomla Articles Guide

Updated 2026-10-15 · Online version: https://claude.ai/code/artifact/65551dff-87b8-448b-b93a-4d1b96257dfc

## Before you start

Articles are the pages of text and pictures that make up most of a Joomla site. You manage them in the administrator under **Content → Articles**. Every article belongs to one **category**, which works like a folder.

**What you can do depends on your user group:**

| Group | Can |
| --- | --- |
| Author | Write new articles and edit their own |
| Editor | Everything an Author can, plus edit anyone's articles |
| Publisher | Everything an Editor can, plus publish, unpublish and feature articles |
| Manager, Administrator, Super Users | Everything, including trash, delete and article settings |

If a button in this guide is missing for you, your group does not allow that action; ask your site administrator.

The screenshots come from a test site at `http://localhost:3000` and use sample articles named **Guide sample**. On your site you will see your own address and articles.

## Open Articles and find your way around

1. In the left menu, click **Content → Articles**. The **+** next to it opens a new article straight away.

   ![Step 1: Content and Articles in the left menu](img/list-01-menu-empty.png)

2. On a new site the screen says **No Articles have been created yet.** Click **Add your first article** to start, or **Learn More** for Joomla's own help.

   ![Step 2: the empty Articles screen](img/list-02-empty-state.png)

3. Once you have articles, the screen shows a list:
   - **New** (3a) starts a new article.
   - **Actions** (3b) works on the articles you tick: publish, unpublish, feature, archive, trash and more.
   - The search bar (3c) finds, filters and sorts articles.
   - The list (3d) shows each article with its **Featured** and **Status** icons, title, alias, category, access, author, date, views (**Hits**) and **ID**. Click a title to edit the article.

   ![Step 3: the Articles list with toolbar, search bar and columns](img/list-03-overview.png)

**Options** (top right) holds site-wide article settings and is for administrators. **Help** opens Joomla's help for this screen.

## Create a category

Categories group related articles, such as News, Events or Help. Create the category before you write articles for it. Every site already has one called **Uncategorised**.

1. In the left menu, click **Content → Categories** (1a), then click **New** (1b).

   ![Step 1: the Categories menu item and the New button](img/cat-01-new.png)

2. Type a name in **Title** (2a), for example `News`. Leave **Alias** empty; Joomla fills it in from the title. Click **Save & Close** (2b).

   ![Step 2: enter the category title and click Save & Close](img/cat-02-form.png)

3. Joomla shows **Category saved.** (3a) and the new category appears in the list with a green tick, which means it is published (3b).

   ![Step 3: the saved message and the new category in the list](img/cat-03-saved.png)

A category can also have a description, a parent category (to make sub-categories) and its own permissions. Articles in an unpublished category do not show on the site, even if the articles themselves are published.

## Write and save an article

1. Go to **Content → Articles** and click **New**. On an empty site you can also click **Add your first article**.

   ![Step 1: the New button on the Articles screen](img/art-01-new.png)

2. Type the headline in **Title** (2a). Write the text in **Article Text** (2b). The editor works like a word processor: use the toolbar for bold, italic, lists and alignment, and the **Paragraph** list for headings. Leave **Alias** empty; Joomla makes it from the title and uses it in the page address.

   ![Step 2: the Title field and the text editor](img/art-02-title-text.png)

3. Check the settings on the right:
   - **Status** (3a): **Published** shows the article on the site; **Unpublished** keeps it as a draft.
   - **Category** (3b): choose where the article belongs. This field is required.
   - **Featured** (3c): **Yes** also shows it in featured lists, often the home page.
   - **Access** (3d): **Public** is everyone; **Registered** means logged-in visitors only.
   - **Tags** (3e): optional keywords that link related articles.

   ![Step 3: Status, Category, Featured, Access and Tags](img/art-03-settings.png)

4. Choose how to save:
   - **Save** (4a) saves and keeps the article open.
   - **Save & Close** (4b) saves and returns to the list.
   - The arrow next to it (4c) has **Save & New**, to start another article right away, and **Save to Menu**, to add the article to a site menu. After the first save it also offers **Save as Copy**.
   - **Cancel** (4d) leaves without saving.

   ![Step 4: the Save, Save & Close, extra save options and Cancel buttons](img/art-04-save-buttons.png)

5. After **Save**, Joomla shows **Article saved.** The alias is now filled in, and new buttons appear at the top: **Close**, **Versions**, **Preview** and **Accessibility Check**.

   ![Step 5: the Article saved message and the extra toolbar buttons](img/art-05-created.png)

Always leave an article with **Save & Close**, **Close** or **Cancel**. If you close the browser tab instead, the article stays locked for others; see **Find, filter and edit articles**.

## Add images

An article can have two main pictures: the **Intro Image**, shown in article lists and on the home page, and the **Full Article Image**, shown at the top of the article page. You can also place pictures anywhere inside the text.

1. Open the article and click the **Images and Links** tab.

   ![Step 1: the Images and Links tab](img/img-01-tab.png)

2. Under **Intro Image**, click **Select**. In the **Change Image** window, open a folder, click a picture, then click **Select** at the top right. To use a picture from your computer, click **Upload** first.

   ![Step 2: the Change Image window](img/img-02-select.png)

3. The picture now shows in **Intro Image** (3a). Describe it in **Image Description (Alt Text)** (3b); this text is read aloud to blind visitors and helps search engines. Do the same for the **Full Article Image** (3c, 3d). Click **Save** or **Save & Close**.

   ![Step 3: the chosen intro and full article images with their descriptions](img/img-03-fields.png)

4. To put a picture inside the text, go back to the **Content** tab, click where the picture should go, then open **CMS Content** in the editor toolbar and choose **Media**. The same menu has **Read More**, which splits the article into a short intro for lists and the full text.

   ![Step 4: the CMS Content menu with Media and Read More](img/img-04-inline.png)

5. After **Save & Close**, Joomla shows **Article saved.** (5a) and you return to the list (5b).

   ![Step 5: the saved message and the article in the list](img/img-05-saved.png)

Use photos that are no wider than about 1920 pixels and under 500 KB, so pages load quickly. The **X** next to **Select** removes a picture.

## Publish, unpublish and schedule

Only **Published** articles show on the site. You can change the status in the article (the **Status** field on the **Content** tab) or straight from the list.

1. In the Articles list, click the icon in the **Status** column to switch an article between published (green tick) and unpublished (grey cross). Point at the icon to see what it will do.

   ![Step 1: the Status icon and its tooltip](img/pub-01-toggle.png)

2. To change several articles at once, tick their boxes (2a), open **Actions** and choose **Publish** (2b) or **Unpublish** (2c).

   ![Step 2: Publish and Unpublish in the Actions menu](img/pub-02-actions.png)

3. To schedule an article, open it, go to the **Publishing** tab and set **Start Publishing** (3a). Optionally set **Finish Publishing** (3b) to hide it again automatically, for example when an offer ends. Click the calendar button to pick a date, then save. Keep **Status** on **Published**.

   ![Step 3: Start Publishing and Finish Publishing dates](img/pub-03-schedule.png)

4. In the list, a scheduled article shows a warning triangle. Point at it to see **Published, but is Pending** with its start and finish dates. It appears on the site by itself at the start date.

   ![Step 4: the pending icon with the scheduled dates](img/pub-04-scheduled.png)

| Status icon | Meaning |
| --- | --- |
| Green tick | Published and visible now |
| Grey cross | Unpublished (draft) |
| Warning triangle | Published, but waiting for its start date, or its finish date has passed |
| Box | Archived |
| Bin | Trashed |

## Feature an article on the home page

Featured articles appear in featured lists. On most Joomla sites, the home page is such a list, so featuring an article puts it on the home page.

1. In the Articles list, find the grey circle in the **Featured** column. Point at it: it says **Unfeatured** and **Toggle featured status**.

   ![Step 1: the Featured toggle of an unfeatured article](img/feat-01-toggle.png)

2. Click the circle. Joomla shows **Article featured.** (2a) and the circle becomes a yellow star (2b). Click the star again to unfeature the article. You can also use **Actions → Feature** for several articles, or set **Featured** to **Yes** inside the article.

   ![Step 2: the Article featured message and the yellow star](img/feat-02-featured.png)

3. To see only featured articles, open **Filter Options** and choose **Featured Articles** in the first filter (3a). The list then shows just the featured ones (3b). Click **Clear** to see all articles again.

   ![Step 3: the Featured Articles filter and the featured article](img/feat-03-featured-list.png)

A featured article also needs **Status: Published** to show on the home page.

## Find, filter and edit articles

1. Type part of a title in **Search** and press Enter or click the magnifier (1a). The list shows only matching articles (1b). Tips: `id:12` finds article number 12, `author:Anna` finds articles by an author, `content:holiday` searches the text.

   ![Step 1: searching for an article](img/find-01-search.png)

2. Click **Filter Options** (2a) to narrow the list by featured, status, category, access, author, checked out, tag or level (2b). Click **Clear** (2c) to remove the search and all filters.

   ![Step 2: Filter Options and Clear](img/find-02-filters.png)

3. Change the order with the sort list (3a), or click a column heading such as **Title** (3b); click it again to reverse the order. The number list (3c) sets how many articles show per page.

   ![Step 3: the sort list, a sortable column heading and the per-page list](img/find-03-sort.png)

4. A padlock next to a title means someone has the article open, or closed the browser without saving. Point at the padlock to see who and since when. Others cannot edit the article until it is checked in.

   ![Step 4: a locked article and its tooltip](img/find-04-locked.png)

5. If you are sure nobody is still working on it, tick the article (5a), open **Actions** (5b) and choose **Check-in** (5c). You can also click the padlock itself if it is your own lock.

   ![Step 5: Check-in in the Actions menu](img/find-05-checkin.png)

6. To edit, click the article's title. Make your changes and click **Save & Close**.

   ![Step 6: click a title to open the article](img/find-06-open.png)

The list remembers your search, filters and sort order until you click **Clear**. If an article seems to be missing, check that no filter is still active.

## Move, copy, archive, trash and restore

1. To move or copy articles to another category, tick them, open **Actions** and choose **Batch**. In **Copy or Move to Category**, pick the category and choose **Move** or **Copy**, then click **Process**. The same window changes the access level or adds and removes tags for all ticked articles at once.

   ![Step 1: the Batch window](img/org-01-batch.png)

2. Tick an article (2a) and open **Actions**. **Archive** (2b) keeps an old article on the site's archive pages but out of normal lists. **Trash** (2c) removes it from the site but keeps it in the trash, so you can still bring it back.

   ![Step 2: Archive and Trash in the Actions menu](img/org-02-menu.png)

3. To see the trash, open **Filter Options** and choose **Trashed** in the status filter (3a). Trashed articles show a bin icon (3b). Only here does the **Delete** button (3c) appear: it removes the ticked articles for good and cannot be undone.

   ![Step 3: the Trashed filter, a trashed article and the Delete button](img/org-03-trashed.png)

4. To restore an article from the trash, tick it and choose **Actions → Publish** (or **Unpublish** to restore it as a draft). Joomla shows **Article published.** Click **Clear** to return to the normal list.

   ![Step 4: the message after restoring an article](img/org-04-restored.png)

Prefer **Unpublish** or **Archive** over **Delete**: they keep the article and its history in case you need it later.

## Versions and preview

Joomla keeps the last 10 saved versions of each article, so you can see what changed and go back. Both buttons appear once an article has been saved.

1. Open the article. Click **Versions** (1a) to see its history, or **Preview** (1b) to see how it will look on the site.

   ![Step 1: the Versions and Preview buttons](img/ver-01-buttons.png)

2. The **Versions** window lists every saved version with its date, **Version Note**, author and size. A star marks the current version. Tick a version and click **Preview** to view it, tick two and click **Compare** to see the differences, or click **Restore** to load an older version back into the form (then save). **Keep On/Off** protects a version from being removed when the limit of 10 is reached.

   ![Step 2: the Versions window](img/ver-02-history.png)

3. **Preview** shows the article in the site's design, including images, before your visitors see it. Close the window with the **X**.

   ![Step 3: the Preview window](img/ver-03-preview.png)

Type a short **Version Note** on the **Content** tab before saving, such as "Added images". It makes the right version easy to find later.

## Search engine basics: alias and meta description

Two fields help your articles look good in Google and other search engines.

1. **Alias** is the part of the page address that comes from the title, such as `guide-sample-welcome-to-our-site`. Joomla fills it in on the first save. Keep it short and avoid changing it after the article is published, because old links and search results would stop working.

   ![Step 1: the Alias field](img/seo-01-alias.png)

2. On the **Publishing** tab, write a **Meta Description** (2a): one or two sentences that say what the article is about. Search engines often show it under the title in their results. Stay under about 160 characters; the counter shows how many are left. Leave **Robots** (2b) on **Use Global** unless you want to keep an article out of search engines.

   ![Step 2: Meta Description and Robots on the Publishing tab](img/seo-02-meta.png)

When an article is featured, the **Publishing** tab also shows **Start Featured** and **Finish Featured**, to feature it for a limited time.

## Troubleshooting

An article that does not show on the site is almost always one of the first five rows below.

| Problem | Check | Fix |
| --- | --- | --- |
| Article not on the site | **Status** icon in the list | Publish it (green tick) |
| Article not on the site | Warning triangle in **Status** | It is scheduled or expired: change **Start Publishing** / **Finish Publishing** on the **Publishing** tab |
| Article not on the site | Its category | The category must be published too (**Content → Categories**) |
| Visitors cannot see it, you can | **Access** field | Set to **Public**; **Registered** shows it only to logged-in visitors |
| Article not on the home page | **Featured** column | Click the circle to make it a yellow star; it must also be published |
| Padlock next to the title; "checked out" message | Point at the padlock | Ask that person to close it, or use **Actions → Check-in** |
| "Save failed" about the alias | Another article in the same category has the same alias | Change **Alias** to something unique |
| Changes not visible on the site | Your browser or the site cache | Reload the page; ask an administrator to clear the cache |
| Article seems to have disappeared from the list | Search bar and filters | Click **Clear**; check the **Trashed** and **Archived** status filters |
| Saved a wrong change | **Versions** | Restore the previous version and save |
| A button in this guide is missing | Your user group | Ask an administrator for the right permission |
