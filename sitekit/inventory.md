# SiteKit admin inventory

Reviewed 2026-10-15 from `administrator/components/com_sitekit` (1.2.0), `plugins/sitekit/*`,
`plugins/system/sitekit` (1.1.1), `media/com_sitekit/js/*` and `language/en-GB/com_sitekit.ini`.

## Access
- Menu: Components → SiteKit → Dashboard (default) · Reports · Services · Settings (`sitekit.xml`).
- Options → Permissions (toolbar button on Dashboard only, for `core.admin`/`core.options`) (`access.xml`):
  - `core.manage` or `sitekit.viewdashboard`: Dashboard, Reports, Services, report fetch (`DisplayController`, `ReportController`).
  - `sitekit.connect` or `core.admin`: OAuth connect/disconnect, trial start/end, authorize scopes, feature save, verification (`OauthController`, `FeatureController`).
  - `core.admin` only: Settings view and save credentials; others are redirected to Dashboard.
- Connection modes (`OAuthService`): none · trial · trial_expired · byo (own client). Banners on every screen follow the mode.

## Screens
### Dashboard (`tmpl/dashboard/default.php`)
- Trial / trial-ended banner → Open Settings.
- Search traffic card (only when Search Console is ready): 28-day chart + top queries (`dashboard.js`), "View Search Console report".
- Setup: 1 Connect Google (Open Settings | Ready) · 2 Google account (Connect with Google | Trial/Connected + email) · 3 Configure core features (View Services).
- Status: Credentials Ready/Missing · Google account Connected/Not connected.
- Features table: Connected / Installed / Add-on (not installed).

### Settings (`tmpl/settings/default.php`, core.admin)
- Try with my Google account: Try with my Google (`oauth.trialStart`) / End trial (`oauth.trialDisconnect`); trial email, views left, end date.
- Your Google Cloud OAuth client (production): Client ID, Client Secret (masked `********` keeps current), Authorized redirect URI (read-only + Copy), Save & Close (`oauth.saveCredentials`).
- Connection: Connect with Google (`oauth.authorize`) / Connected + email + Disconnect (`oauth.disconnect`) / trial hint.
- Setup checklist (6 lines of help text).
- Redirect URI = `<site root>administrator/index.php?option=com_sitekit&task=oauth.callback`.

### Services (`tmpl/services/default.php`)
- Warning when not connected (→ Settings); trial note about using the owning Google account.
- One card per feature, badge Connected / Installed / Add-on (not installed) + install hint.
- Authorize Google scopes (own client only; Search Console, Analytics, Verification).
- Site Verification: Site URL to verify → Save; status Not started / Pending / Verified; token shown; Get META token (`feature.prepareVerification`), Verify with Google (`feature.verify`).
- Search Console: property dropdown (URL-prefix and `Domain:` entries, permission level, suggested match) → Save.
- Analytics 4: GA4 property dropdown, Measurement ID (G-…) → Save.
- Tag Manager: GTM Container ID → Save (no Google sign-in needed).
- PageSpeed (add-on): Test URL → Save. Google Ads (add-on): Conversion ID (AW-…) → Save.
- "Connected" means: Verification = scope + verified; Search Console = scope + property; Analytics = scope + property; Tag Manager = container ID set.

### Reports (`tmpl/reports/default.php`, `reports.js`)
- Report picker (Search Console, Analytics 4, PageSpeed; plugin installed and enabled) → Load.
- Date range 7/14/28/90 days and Page URL filter (Search Console and Analytics only); Refresh; Cached/Live badge; ~60-minute cache; Open Search Console link.
- Search Console: Clicks, Impressions, Average CTR, Average position vs previous period; daily chart; Top queries; Top pages.
- Analytics 4: Users, Sessions, Page views, Engagement rate, Avg. session duration vs previous; users/sessions chart; Traffic channels; Devices; Countries; Top pages.
- PageSpeed: mobile/desktop scores, lab data (LCP/CLS/TBT), field data, How to improve.
- States: Gathering data (up to 48 h), empty, trial ended lock. Trial allows only Search Console and Analytics APIs (`GoogleApiClient::isTrialAllowedUrl`).

## Public site
`plg_system_sitekit` (System - SiteKit Tags), `onBeforeCompileHead`, site client only, adds:
verification meta (pending/verified), GA4 gtag (Measurement ID), GTM container, Ads tag (add-on). Works on localhost except verification.

## Outside the component
- System → Plugins: 5 SiteKit plugins; a disabled feature plugin disappears from Reports.
- Uninstall drops `#__sitekit_oauth` and `#__sitekit_settings`.

## Messages (troubleshooting)
Settings saved · Google account connected/disconnected · Trial connected/disconnected · Feature settings saved ·
Verification token saved / verified · Invalid OAuth state · Token exchange/refresh failed (HTTP x) · No refresh token ·
Search Console / GA4 not set up · Trial ended / feature not in trial · Google API request failed (HTTP x).

## Gaps
- `report.clearCache` task and "Refresh all" string exist but no button calls them.
- Settings submenu is visible to users without `core.admin`; they are redirected to Dashboard.
- PageSpeed and Ads are in the catalog but their plugins are not installed on this site.
- Options screen (com_config) title shows the untranslated key `com_sitekit_configuration`.
- Trial service `https://thepixel.dev/api/sitekit/*` returns 404 (checked 2026-10-15), so the trial cannot start.
- Once your own client is connected, the trial card is hidden on Settings.
