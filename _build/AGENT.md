# Mookmati Instagram-to-website agent

Instructions for the scheduled run that keeps mookmati.in in step with new product posts on instagram.com/mookmatistudio.

## Source of truth
- Website repository: github.com/reviewstoday-ai/Mookmati (GitHub Pages, served at mookmati.in).
- Product catalogue: `_build/products.json` (newest first). Each product's `instagram` field records the post it came from.
- Build: `python3 _build/site.py` regenerates every page, the sitemap and llms.txt from the catalogue.

## Steps
1. Clone the repository and read `_build/products.json`. Collect every `instagram` URL already listed.
2. Open instagram.com/mookmatistudio in Chrome (Claude in Chrome). List the post and reel links on the profile.
3. For each post not already in the catalogue, read its caption. Treat it as a **product launch** only if the caption states a price (for example "Only 950/-" or "Rs 1,500") and describes an item for sale. Skip greetings, quotes and announcements.
4. For each new product, add an object at the top of the right category list in `products.json`:
   - `code`: next free code in that category (bedsheets use MK-BS-###).
   - `slug`: short lowercase words joined by hyphens, starting with the category, e.g. `bedsheet-indigo-butti`.
   - `name`, `price` (digits with Indian commas, no rupee sign), `title`, `note`, `lead`, `points`, `desc`: written only from facts in the caption. Never invent material, size, dye or pillow-cover claims.
   - Shipping wording for bedsheets: use "Free shipping across India on bedsheet orders above Rs 1,000" (Chirag's shipping policy), even if the caption says free shipping.
   - `instagram`: the post URL. `added`: today's date.
   - Categories: bedsheets, sarees, handloom, jewellery, home-decor, serveware, handicrafts. If a category list does not exist yet, create it.
5. Save the product photos of the post (usually 3 slides; for a reel, take 2 to 3 clear still frames of the bedsheet):
   - Main photo: the first slide that shows the product, saved as `images/<code>.webp` (also `.jpg`).
   - Extra photos: each other slide that shows the product (actual product, close-up of the print, room view), saved in post order as `images/<code>-2.jpg`, `images/<code>-3.jpg`, and so on (also `.webp`). The build picks these up automatically and shows them under the main photo.
   - Skip slides that are only text or an information card (price, size, "Order now").
   - For every photo: remove Instagram's sign-up overlay, then capture only the photo area. Leave out the carousel arrow, the counter badge (for example "2 / 3"), slide labels such as "Representative image" or "Actual product", logo badges, the cursor and any text banner. A reliable way is to draw the slide image onto a canvas in a full-page overlay and zoom-capture that.
6. Run `python3 _build/site.py`. Check that the new product page exists, appears on shop.html and in sitemap.xml, and that no image is broken.
7. Publish:
   - If this session can push to the repository, commit with message `Add <name> from Instagram` and push to `main`.
   - Otherwise, zip only the changed and new files, send the zip to Chirag, and tell him to upload them with "Add file > Upload files" (all photos, including the `-2` and `-3` ones, go inside the `images` folder).
8. Tell search engines, only when a product was added and the site is live (wait until the new page loads on mookmati.in):
   - Google Search Console (property sc-domain:mookmati.in, already signed in in Chrome): use "Inspect any URL" on each new product page and on https://mookmati.in/bedsheets.html (or the product's category page), then click "Request indexing". Google allows only a few requests a day; if it refuses, note it in the summary and move on.
   - Bing Webmaster Tools (bing.com/webmasters, site https://mookmati.in/): open URL Submission, click "Submit URLs", and submit each new product page plus https://mookmati.in/shop.html and https://mookmati.in/.
9. Message Chirag with a short summary: products added (name, price, link), search engine submissions done, or "No new products today". Follow his formatting preferences: plain words, bullets, no em dashes, and a closing two-line "In plain terms" summary inside <<< NS >>> markers.

## Rules
- Never remove or change an existing product unless Chirag asks.
- If a caption is unclear (no price, several products, or the photo is a poster rather than the product), add nothing for that post and list it in the summary for Chirag to decide.
- If Chrome is not reachable, do nothing and tell Chirag the check could not run.
