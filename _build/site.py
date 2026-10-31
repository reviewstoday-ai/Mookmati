"""Builds the live static Mookmati site into /home/claude/mookmati-live."""
import os, re, shutil, urllib.parse

import json, datetime
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root
CSS_SRC = os.path.join(OUT, "_build", "base.css")
CATALOG = json.load(open(os.path.join(OUT, "_build", "products.json"), encoding="utf-8"))
TODAY = datetime.date.today().isoformat()
WA = "919456601984"
IG = "mookmatistudio"
IG_URL = f"https://www.instagram.com/{IG}/"
FB_URL = "https://www.facebook.com/profile.php?id=61595446956987"
X_URL = "https://x.com/mookmati"
DOMAIN = "https://mookmati.in"

def wa(msg=None):
    return f"https://wa.me/{WA}" + ("" if not msg else "?text=" + urllib.parse.quote(msg))

CATS = [
    ("bedsheets", "Bedsheets", "Hand block-printed cotton for restful nights."),
    ("sarees", "Sarees", "Handwoven and hand-printed sarees from across India."),
    ("handloom", "Handloom", "Fabrics, stoles and dupattas woven on traditional looms."),
    ("jewellery", "Jewellery", "Handcrafted pieces made by artisan jewellers."),
    ("home-decor", "Home Decor", "Cushions, throws, runners and accents for every room."),
    ("serveware", "Serveware", "Handmade platters, bowls and trays for your table."),
    ("handicrafts", "Handicrafts", "Objects shaped by hand, from clay to wood to metal."),
]

# ---- PRODUCTS come from _build/products.json (newest first) ----
PRODUCTS = {cat: [(p["code"], p["name"], p["note"], p["price"]) for p in items]
            for cat, items in CATALOG.items() if not cat.startswith("_")}

def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

PRODUCT_SLUG = {p["code"]: p["slug"] for cat, items in CATALOG.items() if not cat.startswith("_") for p in items}
def _num(price): return int(price.replace(",", "")) if price else 0
PBY = {p["code"]: dict(p, cat=cat) for cat, items in CATALOG.items() if not cat.startswith("_") for p in items}
CAT_LABEL = {"bedsheets": "Bedsheets", "sarees": "Sarees", "handloom": "Handloom", "jewellery": "Jewellery", "home-decor": "Home Decor", "serveware": "Serveware", "handicrafts": "Handicrafts"}
CAT_SLUG_PREFIX = {"bedsheets": "bedsheet-", "sarees": "saree-", "jewellery": "jewellery-", "home-decor": "table-runner-"}
PAGE_CATS = [c for c in ("bedsheets", "sarees", "jewellery", "home-decor") if CATALOG.get(c)]
def cat_href(s):
    return f"{s}.html" if s in PAGE_CATS else f"shop.html#{s}"
def cat_min_price(s):
    v = sorted(_num(p["price"]) for p in CATALOG.get(s, []) if p.get("price"))
    return v[0] if v else 0
def price_html(code, price):
    mrp = PBY.get(code, {}).get("mrp")
    sp = PBY.get(code, {}).get("set_price")
    if sp:
        return f'&#8377; {price} <span class="popt">runner</span> &middot; &#8377; {sp} <span class="popt">full set</span>'
    return f"&#8377; {price}" + (f' <s class="mrp">&#8377; {mrp}</s>' if mrp else "")
_bs_prices = sorted({_num(p["price"]) for p in CATALOG.get("bedsheets", []) if p["price"]})
def _inr(n): return f"{n:,}"
PRICE_FROM = (f"from \u20b9{_inr(_bs_prices[0])}" if len(_bs_prices) > 1 else f"\u20b9{_inr(_bs_prices[0])}") if _bs_prices else ""
PRICE_FROM_HTML = PRICE_FROM.replace("\u20b9", "&#8377;")
BS_SHIP = "Free shipping across India on bedsheet orders above Rs 1,000"
BS_SIZES = "108 x 90 to 108 x 108 inches"
def _bs_free(price):
    return int(str(price).replace(",", "") or 0) > 1000
def _size_of(title):
    m = re.search(r"(\d+ x \d+)", title or "")
    return (m.group(1) + " inches") if m else "108 x 108 inches"

def product_card(code, name, note, price, idx=0):
    shade = ["", " clay", " madder"][idx % 3]
    photo = None
    for ext in ("png", "jpeg", "jpg", "webp"):
        if os.path.exists(f"{OUT}/images/{code}.{ext}"):
            photo = f"images/{code}.{ext}"
    img = (f'<div class="pimg has-img"><img src="{photo}" alt="{esc(name)}" decoding="async" width="337" height="421"></div>'
           if photo else f'<div class="pimg print{shade}" aria-hidden="true"></div>')
    price_txt = (f"{price_html(code, price)} <span class=\"pship\">{'Made to order, prepaid' if PBY.get(code, {}).get('made_to_order') else ('Free shipping above Rs 1,000' if PBY.get(code, {}).get('cat') == 'bedsheets' else 'Free shipping in India')}</span>") if price else "Price on request"
    msg = f"Hello Mookmati, I would like to order the {name} (code {code})."
    return f"""
        <div class="pcard">
          <a href="{PRODUCT_SLUG.get(code, 'shop')}.html" style="display:block;">{img}</a>
          <div class="pbody">
            <span class="pcode">{code}</span>
            <h4><a href="{PRODUCT_SLUG.get(code, 'shop')}.html" style="color:inherit;text-decoration:none;">{name}</a></h4>
            <p class="pnote">{note}</p>
            <p class="pprice">{price_txt}</p>
            <a class="btn btn-wa btn-sm" href="{wa(msg)}" target="_blank" rel="noopener">Order on WhatsApp</a>
          </div>
        </div>"""

def product_strip(title="Explore our collection", exclude=None):
    lists = [[(p["code"], p["name"], p["price"], p["slug"]) for p in ps if p["code"] != exclude] for cat, ps in CATALOG.items() if not cat.startswith("_")]
    items = []
    for k in range(max([len(l) for l in lists] + [0])):     # newest of each category in turn
        items += [l[k] for l in lists if k < len(l)]
    items = items[:18]
    if not items:
        return ""
    def tile(code, name, price, slug, hidden=False):
        img = next((f"images/{code}.{e}" for e in ("webp", "jpg") if os.path.exists(f"{OUT}/images/{code}.{e}")), "logo-360.webp")
        extra = ' aria-hidden="true" tabindex="-1"' if hidden else ""
        price_txt = f"&#8377; {price}" if price else "Price on request"
        return (f'<a class="stile" href="{slug}.html"{extra}><img src="{img}" alt="{"" if hidden else esc(name)}" loading="lazy" decoding="async" width="220" height="220">'
                f'<span class="sname">{name}</span><span class="sprice">{price_txt}</span></a>')
    reps = max(1, -(-8 // len(items)))          # repeat so one loop is wide enough to fill the screen
    loop = items * reps
    track = "".join(tile(*it, hidden=(i >= len(items))) for i, it in enumerate(loop))
    track += "".join(tile(*it, hidden=True) for it in loop)   # second copy for a seamless loop
    secs = max(20, 5 * len(loop))
    return f"""
  <section class="strip-sec">
    <div class="wrap"><div class="strip-head"><h2>{title}</h2><a href="shop.html">View all</a></div></div>
    <div class="strip" aria-label="{title}"><div class="strip-track" style="animation-duration:{secs}s;">{track}</div></div>
  </section>
"""

def coming_soon(name):
    msg = f"Hello Mookmati, please tell me when your {name} collection is available."
    return f"""
      <div class="box" style="text-align:center;">
        <p style="margin-bottom:14px;"><strong>Coming soon.</strong> Our {name.lower()} collection is being put together with our artisans.</p>
        <a class="btn btn-wa btn-sm" href="{wa(msg)}" target="_blank" rel="noopener">Notify me on WhatsApp</a>
      </div>"""

def live(slug):
    return bool(PRODUCTS.get(slug))

# ---------------- PAGES ----------------
cat_tiles = "".join(
    f'        <a class="cat" href="shop.html#{s}"><span class="name">{n}</span>'
    f'<span class="go">{"Shop now" if live(s) else "Coming soon"}</span></a>\n' for s, n, _ in CATS)

CREDITS = {
    "bedsheets": ("Master artist carves a woodblock for textile printing", "Journyes", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Master_artist_carves_a_woodblock_for_textile_printing.jpg", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "sarees": ("Border of Tangail sari, from the 1970s", "Subornolota", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:Border_of_Tangail_sari,from_the_1970s.jpg", "https://creativecommons.org/licenses/by-sa/3.0/"),
    "handloom": ("Handloom Weaver in an exhibition 3", "Suyash.dwivedi", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Handloom_Weaver_in_an_exhibition_3.jpg", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "jewellery": ("Silver Dogri Jhumka with glass, Bilaspur", "SpeakingArch", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Silver_Dogri_Jhumka_with_glass,_possibly_late_19th-early_20th_century,_Bilaspur.jpg", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "say-hello": ("Krishna's messenger comes to Rukmini", "The San Diego Museum of Art", "Public domain", "https://commons.wikimedia.org/wiki/File:Krishna%27s_messenger_comes_to_Rukmini_(6125058698).jpg", ""),
    "home-decor": ("Peacock-design dhurrie, India", "unknown photographer", "Public domain", "https://commons.wikimedia.org/wiki/File:Peacock-design_dhurrie,_India.JPG", ""),
    "serveware": ("Khurja pottery 3", "Atcelsius", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Khurja_pottery_3.jpg", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "handicrafts": ("Hatima Putul terracotta doll, Asharikandi, Assam", "Nayan j Nath", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Hatima_Putul_Traditional_Terracotta_Doll_from_Asharikandi_Village_Dhubri_Assam_03.jpg", "https://creativecommons.org/licenses/by-sa/4.0/"),
}
photo_tiles = "".join(
    f'        <a class="cat" href="{cat_href(s)}"><img src="images/categories/{s}.webp" alt="{n}" loading="lazy" decoding="async" width="440" height="330"><span class="name">{n}</span>'
    f'<span class="go">{"Shop now" if live(s) else "Coming soon"}</span></a>\n' for s, n, _ in CATS)
def _credit(s, n):
    t, by, lic, src, licurl = CREDITS[s]
    lic_html = f'<a href="{licurl}" target="_blank" rel="noopener">{lic}</a>' if licurl else lic
    return f'{n}: <a href="{src}" target="_blank" rel="noopener">{t}</a> by {by}, {lic_html}'
photo_credits = ('<p style="font-size:12px;color:var(--muted);margin:22px 0 0;line-height:1.6;">Category photos are illustrative, from Wikimedia Commons, cropped. '
                 + "; ".join([_credit(s, n) for s, n, _ in CATS] + [_credit("say-hello", "Say hello")]) + ".</p>")

home_credits = ('<p style="font-size:12px;color:var(--muted);margin:22px 0 0;line-height:1.6;">Category photos are illustrative, from Wikimedia Commons, cropped. '
                + "; ".join(_credit(s, n) for s, n, _ in CATS) + ".</p>")
bs = PRODUCTS["bedsheets"]
def _ico(name):
    paths = {
        "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/>',
        "ig": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor" stroke="none"/>',
        "wa": '<path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"/><path d="M9 9.2c.3 1.9 2.1 4 4.4 4.9l1.2-1.1 1.6.8-.4 1.3c-3.3.5-7.4-3.4-7.6-6.6l1.3-.5.8 1.6z" fill="currentColor" stroke="none"/>',
        "fb": '<path d="M14 8h3V4.5h-3c-2.5 0-4 1.6-4 4.1V11H7.5v3.5H10V21h3.5v-6.5H16.5l.5-3.5h-3.5V8.8c0-.5.3-.8.5-.8z"/>',
        "x": '<path d="M4 4l16 16M20 4L4 20" stroke-width="1.9"/>',
        "bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    }
    return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'

_live_bs = CATALOG["bedsheets"]
# "New arrival" = the most recently added product in ANY category (ties keep catalogue order, bedsheets first).
_all_new = [(p.get("added", ""), -i, cat, p) for i, (cat, p) in enumerate((c, q) for c, lst in CATALOG.items() if isinstance(lst, list) for q in lst)
            if p.get("price") and os.path.exists(f"{OUT}/images/{p['code']}.webp")]
_, _, _newest_cat, _newest = max(_all_new, key=lambda t: (t[0], t[1]))
_newest_ship = ("free shipping on bedsheet orders above Rs 1,000" if _newest_cat == "bedsheets"
                else "made to order, free shipping across India" if _newest.get("made_to_order")
                else "free shipping across India")
_bs_hero = _live_bs[1] if (_newest_cat == "bedsheets" and len(_live_bs) > 1) else _live_bs[0]
HERO_SLIDES = [
    ("indigo", "New arrival", _newest["name"], _newest["lead"], f"&#8377; {_newest['price']}, {_newest_ship}",
     f"{_newest['slug']}.html", "Shop now", f"images/{_newest['code']}.webp", _newest["name"]),
    ("madder", "Hand block-printed in Rajasthan", "Bedsheets that carry the touch of a human hand",
     "Pure cotton, printed one wooden block at a time.", f"Prices {PRICE_FROM_HTML}", "bedsheets.html", "Shop bedsheets",
     f"images/{_bs_hero['code']}.webp", "Hand block-printed cotton bedsheet"),
    ("clay", "Visit our store", "Mookmati, The Silent Earth Studio",
     "See and feel every piece in person at GF193, Gaur City Center, Noida Extension.", "Call or WhatsApp +91 94566 01984", "contact.html", "Get directions",
     "logo-360.webp", "Mookmati logo"),
]
def _slide(i, tone, eyebrow, title, text, price, href, cta, img, alt):
    return f"""
      <div class="hslide {tone}" style="animation-delay:{i * 6}s;"{' aria-hidden="true"' if i else ''}>
        <div class="htext">
          <span class="heyebrow">{eyebrow}</span>
          <h2>{title}</h2>
          <p>{text}</p>
          <p class="hprice">{price}</p>
          <a class="hbtn" href="{href}"{' tabindex="-1"' if i else ''}>{cta}</a>
        </div>
        <div class="himg"><img src="{img}" alt="{'' if i else esc(alt)}" {'fetchpriority="high"' if not i else 'loading="lazy"'} decoding="async"></div>
      </div>"""
hero_html = "".join(_slide(i, *sl) for i, sl in enumerate(HERO_SLIDES))
hero_dots = "".join(f'<span style="animation-delay:{i * 6}s;"></span>' for i in range(len(HERO_SLIDES)))

def _find_card(s, n):
    if live(s):
        href, cap = cat_href(s), (f"Starting &#8377;{_inr(cat_min_price(s))}" if cat_min_price(s) else "Shop now")
    else:
        href, cap = f"shop.html#{s}", "Coming soon"
    return (f'<a class="fcard" href="{href}"><img src="images/categories/{s}.webp" alt="{n}" loading="lazy" decoding="async" width="440" height="330">'
            f'<span class="fcap"><em>{n}</em><span>{cap}</span></span></a>')
find_cards = "".join(_find_card(s, n) for s, n, _ in CATS)

home = f"""
  <h1 class="sr">Mookmati, The Silent Earth Studio: hand block-printed cotton bedsheets and handmade goods</h1>
  <section class="hero2" aria-label="Featured">
    <div class="hslides">{hero_html}
    </div>
    <div class="hdots" aria-hidden="true">{hero_dots}</div>
  </section>
{product_strip("New Arrivals")}
  <section class="finds-sec">
    <div class="wrap">
      <div class="finds">
        <h2 class="ftitle">Fantastic<br>Finds</h2>
        <div class="frow">{find_cards}</div>
      </div>
    </div>
  </section>

  <section class="duo-sec">
    <div class="wrap duo">
      <a class="dbanner" href="bedsheets.html"><img src="images/categories/bedsheets.webp" alt="Artisan carving a wooden printing block" loading="lazy" decoding="async"><span class="dtext"><strong>ONE BLOCK AT A TIME</strong><em>Hand block-printed cotton bedsheets</em><span class="dbtn">Explore now</span></span></a>
      <a class="dbanner" href="about.html"><img src="images/categories/handloom.webp" alt="Weaver at a handloom" loading="lazy" decoding="async"><span class="dtext"><strong>GUIDED BY AHIMSA</strong><em>The story behind Mookmati</em><span class="dbtn">Read our story</span></span></a>
    </div>
  </section>

  <section class="promo print madder">
    <div class="wrap promo-in">
      <div>
        <span class="peyebrow">Free shipping across India, bedsheets above Rs 1,000</span>
        <h2>The Art of Ordering Simply</h2>
        <p>Pick a piece, tap Order on WhatsApp, and we confirm price, stock and delivery with you personally.</p>
      </div>
      <div class="pbtns">
        <a class="hbtn light" href="shop.html">Shop now</a>
        <a class="hbtn ghost" href="{wa('Hello Mookmati, I would like to know more about your products.')}" target="_blank" rel="noopener">Chat on WhatsApp</a>
      </div>
    </div>
  </section>

  <section class="story-sec">
    <div class="wrap split">
      <div>
        <span class="eyebrow">Our story</span>
        <h2>Named after the silent earth</h2>
        <p>Mookmati takes its name from <em>Mookmati</em>, the epic by Acharya Vidyasagar Ji. At its heart is humble clay, shaped through patience into something useful and beautiful.</p>
        <p>We choose what we sell in the same spirit. Every piece is made by hand. Every choice starts with one question: does this cause harm?</p>
        <a class="btn btn-dark" href="about.html">Read our story</a>
      </div>
      <div class="vlist">
        <div><span class="num">01</span><h3>Made by hand</h3><p>Every piece passes through an artisan's hands.</p></div>
        <div><span class="num">02</span><h3>Gentle by choice</h3><p>Natural materials and dyes wherever the craft allows.</p></div>
        <div><span class="num">03</span><h3>Fair to makers</h3><p>We work directly with artisans, so more of every sale reaches them.</p></div>
      </div>
    </div>
  </section>

  <section class="igband">
    <div class="wrap" style="text-align:center;">
      <a class="ighandle" href="{IG_URL}" target="_blank" rel="noopener">{_ico("ig")} @{IG}</a>
      <p>New arrivals, artisan stories and behind-the-scenes from our studio.</p>
      <div class="iggrid">""" + "".join(f'<a href="{IG_URL}" target="_blank" rel="noopener"><img src="images/{p["code"]}.webp" alt="{esc(p["name"])} on Instagram" loading="lazy" decoding="async"></a>' for p in _live_bs[:6]) + """</div>
    </div>
  </section>
"""

shop = """
  <section class="pagehead print">
    <div class="wrap">
      <h1>Shop</h1>
      <p>Every product is handmade. Tap "Order on WhatsApp" and we will confirm price, stock and delivery.</p>
    </div>
  </section>
  <nav class="jump"><div class="wrap">
""" + "".join(f'    <a href="#{s}">{n}</a>\n' for s, n, _ in CATS) + '  </div></nav>\n  <div class="wrap">\n'
for i, (s, n, lead) in enumerate(CATS):
    _pl = PRODUCTS.get(s, [])
    body = (f'<div class="products">{"".join(product_card(*p, idx=i + j) for j, p in enumerate(_pl[:8]))}\n      </div>'
            + (f'<p style="text-align:center;margin-top:22px;"><a class="btn btn-dark" href="{cat_href(s)}">View all {len(_pl)} {n.lower()}</a></p>' if len(_pl) > 8 else "")
            if live(s) else coming_soon(n))
    shop += f"""
    <div class="shopcat" id="{s}">
      <h2>{n}</h2>
      <p class="lead">{lead}{' <a href="bedsheets.html">About our bedsheets</a>' if s == "bedsheets" else (f' <a href="{s}.html">See all {n.lower()}</a>' if s in PAGE_CATS else '')}</p>
      {body}
    </div>
"""
shop += f"""  </div>
  <section><div class="wrap" style="text-align:center;">
    <p style="color:var(--muted);">Looking for something you do not see here? Message us. Many pieces are made in small batches and are not always listed.</p>
    <a class="btn btn-wa" href="{wa('Hello Mookmati, I am looking for a product that is not on the website.')}" target="_blank" rel="noopener">Ask on WhatsApp</a>
  </div></section>
"""

about = f"""
  <section class="pagehead print">
    <div class="wrap">
      <h1>About Mookmati</h1>
      <p>Handmade goods, chosen with care and sold with honesty.</p>
    </div>
  </section>
  <section>
    <div class="wrap split">
      <div>
        <span class="eyebrow">The name</span>
        <h2>Mookmati, the silent earth</h2>
        <p>Our name comes from <em>Mookmati</em>, the epic by Acharya Vidyasagar Ji. Its central figure is ordinary clay, shaped through patience and care into something of use and beauty.</p>
        <p>That idea guides everything we do. We believe the humblest materials, worked by skilled hands, can become objects worth keeping for a lifetime.</p>
      </div>
      <div>
        <figure style="margin:0 0 22px;">
          <img src="images/acharya-vidyasagar-ji.webp" fetchpriority="high" width="410" height="320" alt="Acharya Shri Vidyasagar Ji Maharaj raising his hand in blessing" style="width:100%;height:auto;border-radius:14px;display:block;box-shadow:0 10px 28px rgba(35,50,90,.18);">
          <figcaption style="margin-top:10px;text-align:center;">
            <span style="display:block;font-family:'Cormorant Garamond',serif;font-size:22px;color:var(--indigo);font-weight:600;">Acharya Shri Vidyasagar Ji Maharaj</span>
          </figcaption>
        </figure>
        <p class="quote">Ahimsa is not only what we avoid. It is how we choose to make things.</p>
      </div>
    </div>
  </section>
  <section class="tint">
    <div class="wrap narrow prose">
      <span class="eyebrow">Our approach</span>
      <h2 style="margin-top:0;">Guided by non-violence</h2>
      <p>Mookmati is inspired by non-violence as taught by Acharya Vidyasagar Ji. For us, ahimsa is a practical test we apply to every product we sell.</p>
      <ul>
        <li><strong>Materials.</strong> We favour natural fibres, natural dyes and materials that are gentle on the earth.</li>
        <li><strong>Makers.</strong> We work with artisans and small workshops, and we pay fairly for their skill and time.</li>
        <li><strong>Pace.</strong> Handmade work takes time. We would rather wait for a piece than rush the people making it.</li>
      </ul>
      <p>We began with hand block-printed bedsheets from Rajasthan, and now also offer handloom sarees (never silk) and jewellery. Handloom fabrics, home decor, serveware and handicrafts will follow as we find artisans whose work we are proud to share.</p>
    </div>
  </section>
  <section>
    <div class="wrap narrow prose">
      <span class="eyebrow">Our parent brand</span>
      <h2 style="margin-top:0;">Part of the Sareebari family</h2>
      <p>Mookmati operates under its parent brand, <a href="https://sareebari.com" target="_blank" rel="noopener">Sareebari.com</a>.</p>
      <div class="box"><strong>GST number:</strong> 09AUFPM5087Q1ZP</div>
    </div>
  </section>
  <section>
    <div class="wrap">
      <div class="center">
        <span class="eyebrow">Our crafts</span>
        <h2>What you will find here</h2>
      </div>
      <div class="cats">
{photo_tiles}        <a class="cat" href="contact.html"><img src="images/categories/say-hello.webp" decoding="async" width="440" height="330" alt="Miniature painting of a royal messenger arriving at a palace" loading="lazy"><span class="name">Say hello</span><span class="go">Contact us</span></a>
      </div>
    </div>
  </section>
"""

STORE_LAT, STORE_LNG = 28.605595, 77.4279075
MAP_EMBED = "https://www.google.com/maps?q=Gaur+City+Center,+4+Murti+Chowk,+Gaur+City+1,+Greater+Noida+West+201318&amp;z=17&amp;output=embed"
MAP_DIR = f"https://www.google.com/maps/dir/?api=1&amp;destination={STORE_LAT},{STORE_LNG}"

contact = f"""
  <section class="pagehead print">
    <div class="wrap">
      <h1>Contact us</h1>
      <p>We are a small team and we read every message. The quickest way to reach us is WhatsApp.</p>
    </div>
  </section>
  <section>
    <div class="wrap">
      <div class="contactgrid" style="max-width:1000px;margin:0 auto;">
        <div class="ccard"><h3>WhatsApp</h3><p>Orders, prices, returns and product questions.</p><a class="btn btn-wa" href="{wa('Hello Mookmati, I have a question.')}" target="_blank" rel="noopener">Chat now</a></div>
        <div class="ccard"><h3>Visit our store</h3><p>GF193, Gaur City Center, 4 Murti,<br>Gaur City 1, Greater Noida West<br>Open daily, 10 am to 9 pm</p><a class="btn btn-clay" href="{MAP_DIR}" target="_blank" rel="noopener">Get directions</a></div>
        <div class="ccard"><h3>Instagram</h3><p>New arrivals and artisan stories.</p><a class="btn btn-dark" href="{IG_URL}" target="_blank" rel="noopener">@{IG}</a></div>
      </div>
    </div>
  </section>
  <section id="store-locator">
    <div class="wrap" style="max-width:1000px;">
      <div class="center" style="margin-bottom:20px;"><h2>Store locator</h2><p>Mookmati, GF193 (ground floor), Gaur City Center, 4 Murti Chowk, Gaur City 1, Greater Noida West, Uttar Pradesh 201318. Near Crossings Republik and Noida Extension.</p></div>
      <div class="mapbox"><iframe src="{MAP_EMBED}" title="Map showing Mookmati store at Gaur City Center, Greater Noida West" width="1000" height="420" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
      <p class="center" style="margin-top:14px;font-size:15px;color:var(--muted);">Open every day, 10 am to 9 pm &middot; Call or WhatsApp <a href="tel:+919456601984">+91 94566 01984</a> &middot; <a href="{MAP_DIR}" target="_blank" rel="noopener">Open in Google Maps</a></p>
    </div>
  </section>
  <section class="tint">
    <div class="wrap narrow">
      <div class="center" style="margin-bottom:20px;"><h2>Frequently asked questions</h2></div>
      <details><summary>How do I place an order?</summary><p>Tap "Order on WhatsApp" on any product. We confirm price, stock and delivery time in the chat, then share payment details.</p></details>
      <details><summary>How can I pay?</summary><p>We share payment options on WhatsApp when we confirm your order.</p></details>
      <details><summary>How long does delivery take?</summary><p>We tell you the expected delivery date on WhatsApp before you pay. See our <a href="shipping.html">Shipping Policy</a> for details.</p></details>
      <details><summary>Can I return or exchange a product?</summary><p>We accept returns only for products that arrive damaged, within 7 days of delivery, with an unboxing video. See our <a href="returns.html">Returns and Exchanges</a> policy.</p></details>
      <details><summary>Why does my product look slightly different from the photo?</summary><p>Handmade products vary a little from piece to piece. Colours may also look different on different screens. These variations are part of the craft and are not defects.</p></details>
    </div>
  </section>
"""

def policy(title, intro, body, updated="10 October 2026"):
    return f"""
  <section class="pagehead print">
    <div class="wrap"><h1>{title}</h1><p>{intro}</p></div>
  </section>
  <section>
    <div class="wrap narrow prose">
      <p class="updated">Last updated: {updated}</p>
{body}
    </div>
  </section>
"""

WA_LINK = f'<a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a>'

shipping = policy("Shipping Policy", "How and when your order reaches you.", f"""
      <h2>Where we ship</h2>
      <p>We ship across India, and we also ship internationally.</p>
      <h2>Processing and delivery time</h2>
      <p>Handmade pieces are packed with care, so timelines vary by product. Before you pay, we tell you on {WA_LINK} when your order will be dispatched and when you can expect it.</p>
      <h2>Shipping charges</h2>
      <p>Within India, shipping is free on jewellery, table runners and sarees. Bedsheets ship free on orders above Rs 1,000. For bedsheet orders of Rs 1,000 or less, we confirm the shipping charge on WhatsApp before you pay. International shipping is charged extra, and we confirm the exact charge on WhatsApp before you pay. There are no hidden costs.</p>
      <h2>Tracking</h2>
      <p>We share a tracking link on WhatsApp once your order is dispatched.</p>
      <h2>Damaged in transit</h2>
      <p>Please record an unboxing video when you open your parcel. If it arrives damaged, message us within 7 days of delivery with the video. Without an unboxing video we cannot accept a return. See our <a href="returns.html">Returns and Exchanges</a> policy.</p>
""")

returns = policy("Returns and Exchanges", "Our promise if your product arrives damaged.", f"""
      <div class="box"><strong>In short:</strong> we accept returns only for products that arrive damaged, within 7 days of delivery, and only with an unboxing video. You send the damaged product back to us, and we refund your return shipping charge once we receive it, against the shipping invoice.</div>
      <h2>When we accept a return</h2>
      <ul>
        <li>Returns are accepted <strong>only for damaged products</strong>.</li>
        <li>You must message us within <strong>7 days of delivery</strong>.</li>
        <li>An <strong>unboxing video is a must</strong>. Please record a clear, uncut video while opening the parcel, showing the sealed package and the damage. Without an unboxing video, the product will not be accepted for return.</li>
      </ul>
      <h2>When we cannot accept a return</h2>
      <ul>
        <li>Products that are not damaged, including a change of mind.</li>
        <li>Requests made more than 7 days after delivery.</li>
        <li>Requests without an unboxing video.</li>
      </ul>
      <h2>About handmade variations</h2>
      <p>Handmade products show small differences in print, weave, colour and finish. These are signs of handcraft and are not treated as damage.</p>
      <h2>How to start a return</h2>
      <ol>
        <li>Message us on <a href="{wa('Hello Mookmati, my product arrived damaged. I would like to return it.')}" target="_blank" rel="noopener">WhatsApp</a> within 7 days of delivery with your order details, photos of the damage and the unboxing video.</li>
        <li>We check the video and confirm your return, and share our return address.</li>
        <li>You send the damaged product back to us by courier and keep the shipping invoice.</li>
        <li>Once our team receives the product, we process your return.</li>
      </ol>
      <h2>Return shipping cost</h2>
      <p>The buyer pays the cost of shipping the damaged product back to us. Once our team receives the product, we refund that shipping charge to you, subject to the shipping invoice. Please share a copy of the invoice with us on WhatsApp.</p>
""", updated="20 October 2026")

privacy = policy("Privacy Policy", "What we collect, why, and how we protect it.", f"""
      <p>This policy explains how Mookmati ("we", "us") handles your personal data when you visit mookmati.in or order from us through WhatsApp or Instagram.</p>
      <h2>What we collect</h2>
      <ul>
        <li><strong>Order details:</strong> your name, phone number and delivery address, which you share with us to place an order.</li>
        <li><strong>Messages:</strong> your conversations with us on WhatsApp or Instagram.</li>
      </ul>
      <p>This website does not use forms, logins or tracking cookies. We do not collect card or bank details on this website.</p>
      <h2>Why we use it</h2>
      <ul>
        <li>To confirm, pack and deliver your order.</li>
        <li>To answer your questions and handle returns.</li>
        <li>To keep records required by law, such as invoices.</li>
        <li>To send you updates, only if you have agreed to receive them.</li>
      </ul>
      <h2>Who we share it with</h2>
      <p>We share only what is needed with courier partners to deliver your order. We do not sell your data. Messages sent on WhatsApp and Instagram are also subject to the privacy policies of those platforms.</p>
      <h2>How long we keep it</h2>
      <p>We keep order records for as long as the law requires, and other data only as long as needed for the purposes above.</p>
      <h2>Your rights and complaints</h2>
      <p>You can ask us to access, correct or delete your personal data, or raise any complaint, by messaging us on {WA_LINK}. We will acknowledge your message within 48 hours and resolve it within one month.</p>
      <h2>Changes</h2>
      <p>We may update this policy from time to time. The latest version will always be on this page.</p>
""")

_rows = "".join(
    f"<li><strong>{n}:</strong> " + _credit(s, n).split(": ", 1)[1] + "</li>\n"
    for s, n in [(c[0], c[1]) for c in CATS] + [("say-hello", "Say hello")])
credits = policy("Photo Credits", "Thank you to the photographers whose work helps tell our story.", f"""
      <p>Our product photos are our own. The category and illustration photos below come from Wikimedia Commons and are used under their licences. We have cropped them to fit our layout.</p>
      <h2>Category photos</h2>
      <ul>
{_rows}      </ul>
      <h2>About page</h2>
      <ul>
        <li><strong>Acharya Shri Vidyasagar Ji Maharaj:</strong> <a href="https://commons.wikimedia.org/wiki/File:0521_acaaraya.jpg" target="_blank" rel="noopener">0521 acaaraya</a> by Agniban.com, public domain.</li>
      </ul>
""")

terms = policy("Terms of Use", "The rules for using our website and buying from us.", f"""
      <h2>About these terms</h2>
      <p>mookmati.in is the website of Mookmati. By using this website or placing an order with us, you agree to these terms.</p>
      <h2>Products and prices</h2>
      <p>Product photos are for reference. Handmade items vary slightly from piece to piece. Prices and availability are confirmed on WhatsApp before you pay, and the confirmed price is final.</p>
      <h2>Orders and payment</h2>
      <p>An order is confirmed only after we receive payment. We may decline or cancel an order if an item is out of stock, in which case we refund you in full.</p>
      <h2>Shipping and returns</h2>
      <p>Please read our <a href="shipping.html">Shipping Policy</a> and <a href="returns.html">Returns and Exchanges</a> policy.</p>
      <h2>Intellectual property</h2>
      <p>All photos, text and designs on this website belong to Mookmati or its artisans. Please do not copy them without permission.</p>
      <h2>Governing law</h2>
      <p>These terms are governed by the laws of India.</p>
      <h2>Contact</h2>
      <p>Questions about these terms? Message us on {WA_LINK}.</p>
""")

footer = f"""<footer class="mk mk-footer2">
  <div class="wrap">
    <div class="fcols">
      <div>
        <h4>Let us help you</h4>
        <a href="{wa('Hello Mookmati, I would like to place an order.')}" target="_blank" rel="noopener">Order on WhatsApp</a>
        <a href="contact.html#store-locator">Store locator</a>
        <a href="{wa('Hello Mookmati, I would like to ask about a bulk order.')}" target="_blank" rel="noopener">Bulk orders</a>
        <a href="contact.html">Contact us</a>
      </div>
      <div>
        <h4>Support</h4>
        <a href="contact.html">How to order</a>
        <a href="shipping.html">Shipping and delivery</a>
        <a href="returns.html">Returns and exchanges</a>
        <a href="contact.html">FAQs</a>
      </div>
      <div>
        <h4>Shop</h4>
""" + "".join(f'        <a href="{cat_href(s)}">{n}</a>\n' for s, n, _ in CATS) + f"""      </div>
      <div>
        <h4>About Mookmati</h4>
        <a href="about.html">Our story</a>
        <a href="privacy.html">Privacy policy</a>
        <a href="terms.html">Terms of use</a>
        <a href="credits.html">Photo credits</a>
      </div>
    </div>
    <div class="fbottom">
      <div class="ffollow"><span>Follow us</span><a href="{IG_URL}" target="_blank" rel="noopener" aria-label="Instagram" title="Instagram">{_ico("ig")}</a><a href="{FB_URL}" target="_blank" rel="noopener" aria-label="Facebook" title="Facebook">{_ico("fb")}</a><a href="{X_URL}" target="_blank" rel="noopener" aria-label="X" title="X">{_ico("x")}</a><a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp" title="WhatsApp">{_ico("wa")}</a></div>
      <div class="fstore"><strong>Visit our store</strong><span>GF193, Gaur City Center, Noida Extension &middot; +91 94566 01984</span></div>
    </div>
    <div class="small">&copy; 2026 Mookmati. All rights reserved.</div>
  </div>
</footer>
<a class="mk-float" href="{wa("Hello Mookmati!")}" target="_blank" rel="noopener" aria-label="WhatsApp us">{_ico("wa")}<span>WhatsApp us</span></a>"""

import json
SITE = DOMAIN
def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

ORG = {
  "@context": "https://schema.org", "@type": "HomeGoodsStore", "@id": SITE + "/#store",
  "name": "Mookmati", "alternateName": "Mookmati, The Silent Earth Studio",
  "url": SITE + "/", "logo": SITE + "/logo.png", "image": SITE + "/logo.png",
  "description": "Mookmati, The Silent Earth Studio, sells hand block-printed cotton bedsheets and handmade Indian goods guided by ahimsa (non-violence). Orders on WhatsApp, free shipping across India (bedsheets on orders above Rs 1,000).",
  "telephone": "+91-9456601984",
  "address": {"@type": "PostalAddress", "streetAddress": "GF193, Gaur City Center, 4 Murti, Gaur City 1", "addressLocality": "Greater Noida West", "addressRegion": "UP", "postalCode": "201318", "addressCountry": "IN"},
  "geo": {"@type": "GeoCoordinates", "latitude": 28.605595, "longitude": 77.4279075},
  "hasMap": "https://www.google.com/maps?cid=6880888118234254602",
  "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "10:00", "closes": "21:00"},
  "areaServed": "IN", "currenciesAccepted": "INR",
  "sameAs": [IG_URL, FB_URL, X_URL],
  "contactPoint": {"@type": "ContactPoint", "telephone": "+91-9456601984", "contactType": "sales", "availableLanguage": ["en", "hi"]},
}

PDETAIL = {p["code"]: {"title": p["title"], "lead": p["lead"], "points": p["points"], "desc": p["desc"]}
           for cat, items in CATALOG.items() if not cat.startswith("_") for p in items}

GPC = {"bedsheets": "Home & Garden > Linens & Bedding > Bedding > Bed Sheets",
       "sarees": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing > Saris & Lehengas",
       "jewellery": "Apparel & Accessories > Jewelry",
       "home-decor": "Home & Garden > Linens & Bedding > Table Linens > Table Runners"}

def product_ld(code, name, price, slug, img):
    d = PDETAIL[code]
    return {
      "@context": "https://schema.org", "@type": "Product", "sku": code, "name": name,
      "description": d["desc"], "image": [SITE + "/" + img], "brand": {"@type": "Brand", "name": "Mookmati"},
      **({"material": "Cotton", "size": _size_of(d.get("title"))} if PBY[code]["cat"] == "bedsheets" else ({"material": PBY[code]["fabric"]} if PBY[code].get("fabric") else {})),
      "category": GPC.get(PBY[code]["cat"], "Home & Garden"),
      "countryOfOrigin": "IN",
      "offers": {"@type": "Offer", "url": f"{SITE}/{slug}.html", "price": price.replace(",", ""), "priceCurrency": "INR",
                 "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
                 "seller": {"@id": SITE + "/#store"},
                 **({} if (PBY[code]["cat"] == "bedsheets" and not _bs_free(price)) else {"shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "INR"},
                                     "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "IN"}}}),
                 "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "IN",
                                             "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                                             "merchantReturnDays": 7, "returnMethod": "https://schema.org/ReturnByMail"}},
    }

def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

BS_FAQ = [
 ("What size are Mookmati bedsheets?", "Our bedsheets range from 108 x 90 inches to 108 x 108 inches (king, king plus or super king). Each product page shows its exact size. They fit king beds, and drape generously over queen beds."),
 ("What are the bedsheets made of?", "They are made of 100% pure cotton, which is soft, breathable and cool on warm nights."),
 ("What is hand block printing?", "Artisans press carved wooden blocks dipped in dye onto the cloth, one impression at a time. Small variations in the print are the mark of handwork, not a flaw."),
 ("How much do the bedsheets cost?", f"Our bedsheets are priced {PRICE_FROM} onwards, with free shipping across India on bedsheet orders above Rs 1,000. International shipping is available at an extra charge."),
 ("How do I order?", "Tap “Order on WhatsApp” on any product, or message +91 94566 01984. You can also visit our store at GF193, Gaur City Center, Noida Extension."),
 ("How should I wash a block-printed cotton bedsheet?", "Wash separately in cold water with a mild detergent for the first few washes, and dry in shade to keep the colours fresh."),
]
faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in BS_FAQ]}

def product_img(code):
    for ext in ("webp", "jpg"):
        if os.path.exists(f"{OUT}/images/{code}.{ext}"):
            return f"images/{code}.{ext}"
    return "logo.png"

# Bedsheets category landing page
bs_cards = "".join(product_card(*p, idx=i) for i, p in enumerate(PRODUCTS["bedsheets"]))
bedsheets_page = f"""
  <section class="pagehead print">
    <div class="wrap">
      <h1>Hand Block-Printed Cotton Bedsheets</h1>
      <p>Pure cotton bedsheets from Rajasthan, block printed designs and sized generously at 108 x 90 inches to 108 x 108 inches. Priced {PRICE_FROM_HTML} onwards, with free shipping across India on orders above Rs 1000/-.</p>
    </div>
  </section>
  <section>
    <div class="wrap">
      <div class="products">{bs_cards}
      </div>
    </div>
  </section>
  <section class="tint">
    <div class="wrap narrow prose">
      <h2 style="margin-top:0;">Why choose a Mookmati bedsheet</h2>
      <p>Our bedsheets are made the slow way. In Rajasthan, artisans carve patterns into wooden blocks, dip them in dye and press them onto cotton by hand, one impression at a time. The result is a bedsheet with real character, where every flower carries the touch of the person who printed it.</p>
      <ul>
        <li><strong>Pure cotton:</strong> soft, breathable and cool, ideal for Indian summers and comfortable all year.</li>
        <li><strong>Large size:</strong> 108 x 90 to 108 x 108 inches, which fits king beds with room to tuck in.</li>
        <li><strong>Gentle choices:</strong> natural dyes wherever the craft allows, and no silk. Our work is guided by ahimsa, the path of non-violence taught by Acharya Shri Vidyasagar Ji Maharaj.</li>
        <li><strong>Fair price:</strong> {PRICE_FROM_HTML} onwards, with free shipping across India on bedsheet orders above Rs 1,000.</li>
      </ul>
    </div>
  </section>
  <section>
    <div class="wrap narrow">
      <div class="center" style="margin-bottom:20px;"><h2>Bedsheet questions</h2></div>
""" + "".join(f"      <details><summary>{q}</summary><p>{a}</p></details>\n" for q, a in BS_FAQ) + f"""
      <div style="text-align:center;margin-top:32px;">
        <a class="btn btn-wa" href="{wa('Hello Mookmati, I would like to know more about your bedsheets.')}" target="_blank" rel="noopener">Ask about bedsheets on WhatsApp</a>
      </div>
    </div>
  </section>
"""

# Category landing pages for sarees and jewellery
CAT_INTRO = {
    "sarees": ("Handloom Sarees", "Handwoven mul cotton, Bengal handloom, linen and Ajrakh sarees. No silk: every saree here is chosen in the spirit of ahimsa."),
    "jewellery": ("Jewellery", "Handcrafted earrings, necklace sets and danglers to complete your look."),
    "home-decor": ("Table Runners", "Rajasthani waxed handblock print table runners on 100% pure cotton, made to order."),
}
RUNNER_STORY = f"""
  <section class="tint">
    <div class="wrap narrow prose">
      <span class="eyebrow">Home Decor</span>
      <h2 style="margin-top:0;">Elevate Your Dining Space with the Timeless Charm of Rajasthan &#10024;</h2>
      <p>There is something deeply personal about a beautifully set table. It is where stories are shared, meals are enjoyed, and memories are made. If you want to add a touch of heritage, elegance, and soul to your home, our brand-new Rajasthani Waxed Handblock Print Table Runner Set is exactly what you need.</p>
      <p>Crafted on 100% pure cotton, each piece is a celebration of centuries-old Indian craftsmanship brought straight to your dining room.</p>
      <h2>The Art Behind the Fabric: Waxed Handblock Printing &#127806;</h2>
      <p>Unlike mass-produced machine prints, these table runners are printed entirely by hand using the traditional waxed handblock printing technique.</p>
      <ol>
        <li><strong>Intricate Carving:</strong> Skilled artisans meticulously carve breathtaking Rajasthani motifs into wooden blocks.</li>
        <li><strong>Wax Resist Printing:</strong> Hot wax is applied to the blocks and pressed firmly onto the pure cotton fabric to create a beautiful, crisp resist pattern.</li>
        <li><strong>Natural Dyeing:</strong> The fabric is dyed, and once the wax is washed away, a stunning, intricate design is revealed.</li>
      </ol>
      <p>Because every single piece is handcrafted, no two runners are exactly identical. You aren't just buying table linen, you are bringing a unique piece of wearable art into your home.</p>
      <h2>Versatile Styling Options &amp; Pricing &#128176;</h2>
      <p>Whether you want a simple accent or a complete table transformation, we have the perfect option for your space:</p>
      <ul>
        <li><strong>&#127991;&#65039; The Solo Accent (Only Table Runner): Rs. 750/-</strong><br>Perfect for adding a pop of culture and color to your dining table, console table, or hallway dresser.</li>
        <li><strong>&#127869;&#65039; The Complete Experience (Full Table Runner Set): Rs. 1500/-</strong><br>Includes the gorgeous runner along with matching coordinates to give your dining room a fully styled, premium look.</li>
      </ul>
      <h2>&#9203; Made Exceptionally For You: Available via Prepaid Orders Only</h2>
      <p>In a world of fast fashion and instant gratification, we believe in slow, sustainable luxury.</p>
      <p>We do not hold ready-made factory stock. To minimize waste and support local craft clusters, these pieces are made entirely to order. The moment you place your order, our artisans in Rajasthan begin block-printing your specific fabric.</p>
      <ul>
        <li><strong>&#128179; Payment:</strong> Available via Prepaid Order only on WhatsApp through UPI.</li>
        <li><strong>&#128736;&#65039; Artisan Crafting Time:</strong> Because perfection takes time, please allow a short production window as our artisans hand-dye and finish your set with love.</li>
      </ul>
      <h2>&#128717;&#65039; How to Place Your Order</h2>
      <p>Transform your dining room into a heritage sanctuary. Pick your favourite design above, or tap the button below to secure your piece of Rajasthan&#8217;s artistic history today!</p>
      <p><a class="btn btn-wa" href="{wa('Hello Mookmati, I would like to order a Rajasthani waxed handblock print table runner (prepaid via UPI).')}" target="_blank" rel="noopener">Order on WhatsApp</a></p>
    </div>
  </section>
"""
def category_page(s):
    h1, intro = CAT_INTRO[s]
    cards = "".join(product_card(*p, idx=i) for i, p in enumerate(PRODUCTS[s]))
    return f"""
  <section class="pagehead print">
    <div class="wrap">
      <h1>{h1}</h1>
      <p>{intro} {"Runner Rs. 750, full set Rs. 1,500. Free shipping across India. Prepaid orders on WhatsApp via UPI." if s == "home-decor" else "Free shipping across India. Order on WhatsApp."}</p>
    </div>
  </section>
  <section>
    <div class="wrap">
      <div class="products">{cards}
      </div>
      <div style="text-align:center;margin-top:36px;">
        <a class="btn btn-wa" href="{wa('Hello Mookmati, I would like to know more about your ' + h1.lower() + '.')}" target="_blank" rel="noopener">Ask about {h1.lower()} on WhatsApp</a>
      </div>
    </div>
  </section>
""" + (RUNNER_STORY if s == "home-decor" else "")
CAT_PAGES = {c: category_page(c) for c in PAGE_CATS if c != "bedsheets"}

def product_gallery(code, n):
    return [f"images/{code}.jpg" if os.path.exists(f"{OUT}/images/{code}.jpg") else product_img(code)] + \
           [f"images/{code}-{k}.jpg" for k in range(2, (n or 1) + 1) if os.path.exists(f"{OUT}/images/{code}-{k}.jpg")]

# Individual product pages
PRODUCT_PAGES = []
for cat in [c for c in CATALOG if not c.startswith("_")]:
    for code, name, note, price in PRODUCTS[cat]:
        p = PBY[code]; d = PDETAIL[code]; slug = PRODUCT_SLUG[code]
        # Bedsheets: main photo is images/<code>.webp; extra Instagram slides are images/<code>-2.jpg, -3.jpg, ... (picked up automatically)
        gal = product_gallery(code, p.get("images")) if cat != "bedsheets" else \
              [product_img(code)] + [f"images/{code}-{k}.jpg" for k in range(2, 10) if os.path.exists(f"{OUT}/images/{code}-{k}.jpg")]
        img = gal[0]; label = CAT_LABEL.get(cat, cat.title())
        msg = f"Hello Mookmati, I would like to order the {name} (code {code})."
        thumbs = ("<div class=\"pgal\">" + "".join(f'<img src="{g}" alt="{esc(name)}, photo {k + 2}" loading="lazy" decoding="async">' for k, g in enumerate(gal[1:])) + "</div>") if len(gal) > 1 else ""
        if p.get("desc_html"):
            detail = f'<div class="pdesc prose">{p["desc_html"]}</div>'
            lead = ""
        else:
            detail = '<ul class="ticks" style="list-style:none;padding:0;">' + "".join(f'<li style="padding-left:24px;position:relative;margin-bottom:8px;"><span style="position:absolute;left:0;top:9px;width:10px;height:10px;border-radius:50%;background:var(--clay);"></span>{x}</li>' for x in d["points"]) + "</ul>"
            lead = f'<p style="font-size:19px;">{d["lead"]}</p>'
        if p.get("set_price"):
            order_btns = (f'            <a class="btn btn-wa" href="{wa(f"Hello Mookmati, I would like to order the {name} (code {code}), only table runner, Rs. {price}. I will pay prepaid via UPI.")}" target="_blank" rel="noopener">Order runner &#8377;{price}</a>\n'
                          f'            <a class="btn btn-wa" href="{wa(f"Hello Mookmati, I would like to order the {name} (code {code}), full table runner set, Rs. {p["set_price"]}. I will pay prepaid via UPI.")}" target="_blank" rel="noopener">Order full set &#8377;{p["set_price"]}</a>')
        else:
            order_btns = f'            <a class="btn btn-wa" href="{wa(msg)}" target="_blank" rel="noopener">Order on WhatsApp</a>'
        ig_btn = f'<a class="btn btn-dark" href="{p["instagram"]}" target="_blank" rel="noopener">See it on Instagram</a>' if p.get("instagram") else f'<a class="btn btn-dark" href="{cat_href(cat)}">More {label.lower()}</a>'
        body = f"""
  <section>
    <div class="wrap">
      <p style="font-size:14px;color:var(--muted);margin-bottom:24px;"><a href="index.html">Home</a> / <a href="{cat_href(cat)}">{label}</a> / {name}</p>
      <div class="split" style="align-items:start;">
        <div><img src="{img}" alt="{esc(d['title'])}" fetchpriority="high" style="width:100%;height:auto;border-radius:14px;display:block;">{thumbs}</div>
        <div>
          <span class="eyebrow">{code}</span>
          <h1 style="font-size:clamp(30px,4.2vw,42px);">{name}</h1>
          {lead}
          <p class="pprice" style="font-size:26px;">{price_html(code, price)}<span class="pship" style="font-size:14px;">{"Made to order. Free shipping across India. Prepaid via UPI on WhatsApp. Please allow a short crafting time." if p.get("made_to_order") else ((BS_SHIP + ". International shipping charged extra.") if cat == "bedsheets" else "Free shipping across India. International shipping charged extra.")}</span></p>
          <div class="btns" style="justify-content:flex-start;margin:14px 0 22px;">
{order_btns}
            {ig_btn}
          </div>
          {detail}
          <p style="font-size:14px;color:var(--muted);margin-top:18px;">Prefer to see it in person? Visit our store at GF193, Gaur City Center, Noida Extension. See our <a href="shipping.html">Shipping</a> and <a href="returns.html">Returns</a> policies.</p>
        </div>
      </div>
    </div>
  </section>
""" + product_strip("You may also like", exclude=code)
        head = ld(product_ld(code, name, price, slug, img)) + "\n" + ld(crumbs([("Home", "/"), (label, "/" + cat_href(cat)), (name, f"/{slug}.html")]))
        PRODUCT_PAGES.append((slug, None, body, f"{d['title']} | Mookmati", d["desc"] + (f" ₹{price}, free shipping in India on bedsheet orders above Rs 1,000." if cat == "bedsheets" else f" ₹{price}, free shipping in India."), head, SITE + "/" + img))

SCHEMA = {
  "index": ld(ORG) + "\n" + ld({"@context": "https://schema.org", "@type": "WebSite", "name": "Mookmati", "url": SITE + "/"}),
  "contact": ld(ORG),
  "about": ld(ORG),
  "bedsheets": ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Hand block-printed cotton bedsheets",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{PRODUCT_SLUG[c]}.html", "name": n} for i, (c, n, _, _) in enumerate(PRODUCTS["bedsheets"])]})
               + "\n" + ld(faq_ld) + "\n" + ld(crumbs([("Home", "/"), ("Bedsheets", "/bedsheets.html")])),
  **{c: ld({"@context": "https://schema.org", "@type": "ItemList", "name": CAT_INTRO[c][0],
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{PRODUCT_SLUG[k]}.html", "name": n} for i, (k, n, _, _) in enumerate(PRODUCTS[c])]})
        + "\n" + ld(crumbs([("Home", "/"), (CAT_LABEL[c], f"/{c}.html")])) for c in CAT_PAGES},
}

LLMS = """# Mookmati, The Silent Earth Studio

> Mookmati (mookmati.in) is an Indian brand selling handmade home textiles and crafts guided by ahimsa (non-violence), inspired by Acharya Shri Vidyasagar Ji Maharaj and his epic Mookmati. Products include handloom cotton, linen and Ajrakh sarees (no silk), jewellery, and hand block-printed 100% cotton bedsheets from Rajasthan priced """ + PRICE_FROM.replace("\u20b9","Rs ") + """ onwards, with free shipping across India on bedsheet orders above Rs 1,000. Orders are placed on WhatsApp (+91 94566 01984) or Instagram (@mookmatistudio). Store: GF193, Gaur City Center, Noida Extension (Greater Noida West), Uttar Pradesh, India.

## Products
- [Hand block-printed cotton bedsheets](https://mookmati.in/bedsheets.html): category overview, sizes, care and FAQs
""" + "".join(f"- [{p['name']}](https://mookmati.in/{p['slug']}.html): {p['desc']} Rs {p['price']}\n" for p in CATALOG["bedsheets"]) + """""" + "".join(f"\n## {CAT_INTRO[c][0]}\n- [{CAT_INTRO[c][0]}](https://mookmati.in/{c}.html): {CAT_INTRO[c][1]}\n" + "".join(f"- [{p['name']}](https://mookmati.in/{p['slug']}.html): Rs {p['price']}\n" for p in CATALOG[c]) for c in CAT_PAGES) + """
- [All products](https://mookmati.in/shop.html): handloom, home decor, serveware and handicrafts coming soon

## About and policies
- [About Mookmati](https://mookmati.in/about.html)
- [Contact and FAQ](https://mookmati.in/contact.html)
- [Shipping](https://mookmati.in/shipping.html): free shipping in India on jewellery and table runners, and on bedsheet orders above Rs 1,000; international shipping charged extra
- [Returns and exchanges](https://mookmati.in/returns.html): returns only for damaged products, within 7 days of delivery, unboxing video required
"""

PAGES = [
    ("index", "Home", home, "Mookmati | Hand Block-Printed Cotton Bedsheets, Handmade in India",
     "Shop hand block-printed 100% cotton bedsheets from Rajasthan, 108 x 90 to 108 x 108 inches, " + PRICE_FROM + " onwards, free shipping in India above Rs 1,000. Handmade goods guided by ahimsa. Order on WhatsApp."),
    ("bedsheets", None, bedsheets_page, "Hand Block-Printed Cotton Bedsheets, 108 x 90 to 108 x 108 | Mookmati",
     "Pure cotton hand block-printed bedsheets from Rajasthan, 108 x 90 to 108 x 108 inches, " + PRICE_FROM + " onwards, free shipping in India on orders above Rs 1,000. Natural dyes, no silk. Order on WhatsApp or visit our Noida Extension store."),
] + [(c, None, CAT_PAGES[c], f"{CAT_INTRO[c][0]} | Mookmati",
      CAT_INTRO[c][1] + " Free shipping across India. Order on WhatsApp.") for c in CAT_PAGES] + [
    ("shop", "Shop", shop, "Shop | Mookmati",
     "Shop hand block-printed cotton bedsheets, handloom sarees (no silk) and jewellery. Handloom, home decor, serveware and handicrafts coming soon. Order on WhatsApp. Free shipping in India, bedsheets above Rs 1,000."),
    ("about", "About", about, "About Us | Mookmati",
     "Mookmati is named after Acharya Vidyasagar Ji's epic and guided by ahimsa, the path of non-violence."),
    ("contact", "Contact", contact, "Contact Us | Mookmati",
     "Contact Mookmati on WhatsApp +91 94566 01984, Instagram @mookmatistudio, or visit our store at GF193, Gaur City Center, Noida Extension."),
    ("shipping", None, shipping, "Shipping Policy | Mookmati", "How Mookmati ships orders within India."),
    ("returns", None, returns, "Returns and Exchanges | Mookmati", "Mookmati's returns and exchanges policy."),
    ("privacy", None, privacy, "Privacy Policy | Mookmati", "How Mookmati handles your personal data."),
    ("credits", None, credits, "Photo Credits | Mookmati", "Credits for photos used on mookmati.in."),
    ("terms", None, terms, "Terms of Use | Mookmati", "Terms of using mookmati.in and ordering from Mookmati."),
]
PAGES = [p + ((SCHEMA.get(p[0], ""), SITE + "/logo.png") if len(p) == 5 else ()) for p in PAGES] + PRODUCT_PAGES

HEADER_CSS = """
body{margin:0;background:#faf6ee;}
.mk-bar{background:#8e2f2a;color:#faf6ee;text-align:center;font:600 13px Mulish,sans-serif;padding:8px 12px;letter-spacing:.04em;}
.mk-bar a{color:#faf6ee;}
.mk-head{background:#faf6ee;border-bottom:1px solid #e2d6c3;font-family:Mulish,sans-serif;position:sticky;top:0;z-index:60;box-shadow:0 2px 10px rgba(35,50,90,.06);}
.mk .jump{position:static;}
.mk .strip-sec{padding:36px 0 40px;border-bottom:1px solid #e2d6c3;}
.mk .strip-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:16px;}
.mk .strip-head h2{margin:0;font-size:clamp(26px,3.5vw,34px);}
.mk .strip-head a{font:700 14px Mulish,sans-serif;color:#b5653f;}
.mk .strip{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 4%,#000 96%,transparent);mask-image:linear-gradient(90deg,transparent,#000 4%,#000 96%,transparent);}
.mk .strip-track{display:flex;gap:18px;width:max-content;padding:4px 0;animation:mkstrip linear infinite;}
.mk .strip:hover .strip-track,.mk .strip:focus-within .strip-track{animation-play-state:paused;}
.mk .stile{flex:0 0 220px;display:block;background:#fff;border:1px solid #e2d6c3;border-radius:14px;overflow:hidden;text-decoration:none;color:#2b2420;transition:transform .2s,box-shadow .2s;}
.mk .stile:hover{transform:translateY(-3px);box-shadow:0 8px 20px rgba(35,50,90,.14);}
.mk .stile img{width:220px;height:220px;object-fit:cover;display:block;}
.mk .stile .sname{display:block;padding:10px 12px 2px;font:600 15px Mulish,sans-serif;line-height:1.3;}
.mk .stile .sprice{display:block;padding:0 12px 12px;font:700 15px Mulish,sans-serif;color:#b5653f;}
@keyframes mkstrip{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){.mk .strip{overflow-x:auto;}.mk .strip-track{animation:none;}}
@media (max-width:600px){.mk .stile{flex-basis:160px;}.mk .stile img{width:160px;height:160px;}}
.mk-head .in{max-width:1180px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;}
.mk-logo{font:600 30px 'Cormorant Garamond',serif;color:#23325a;text-decoration:none;line-height:1;display:flex;align-items:center;gap:12px;}
.mk-logo img{height:60px;width:auto;border-radius:6px;display:block;}
.mk-logo small{display:block;font:600 11px Mulish,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#b5653f;margin-top:4px;}
.mk .pship{display:block;font-size:12px;font-weight:600;color:#1f7a4d;margin-top:2px;}
.mk-nav{display:flex;gap:18px;flex-wrap:wrap;}
.mk-nav a{color:#2b2420;text-decoration:none;font-weight:600;font-size:15px;}
.mk-nav a:hover,.mk-nav a.on{color:#b5653f;}
@media (max-width:480px){.mk .cat{padding:16px;}.mk .cat .name{font-size:22px;}}
/* ---- Fabindia-style layout ---- */
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);}
.mk-head{background:#fff;}
.mk-head .in{padding:10px 20px;flex-wrap:nowrap;}
.mk-icons{display:flex;gap:18px;align-items:center;}
.mk-icons a{color:#8e2f2a;display:flex;}
.mk-icons a:hover{color:#23325a;}
.mk-head .mk-nav{display:block;background:#f6efe4;border-top:1px solid #e2d6c3;}
.mk-nav .nin{max-width:1180px;margin:0 auto;padding:0 20px;display:flex;justify-content:space-between;gap:22px;overflow-x:auto;scrollbar-width:none;}
.mk-nav .nin::-webkit-scrollbar{display:none;}
.mk-nav a{white-space:nowrap;padding:11px 0;font-size:15px;font-weight:600;border-bottom:2px solid transparent;}
.mk-nav a.on{color:#8e2f2a;border-bottom-color:#8e2f2a;}
.mk-nav a:hover{color:#8e2f2a;}
.mk section.hero2{padding:0;background:#23325a;position:relative;}
.hslides{display:grid;}
.hslide{grid-area:1/1;display:grid;grid-template-columns:1.1fr .9fr;align-items:center;min-height:440px;opacity:0;visibility:hidden;animation:mkfade 18s infinite;}
.hslide.indigo{background:#23325a;}
.hslide.madder{background:#8e2f2a;}
.hslide.clay{background:#b5653f;}
.hslides:hover .hslide,.hslides:hover ~ .hdots span{animation-play-state:paused;}
.htext{padding:56px 40px 56px max(40px,calc((100vw - 1180px)/2 + 20px));color:#faf6ee;}
.heyebrow{display:inline-block;font:700 12px Mulish,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#f3d9b8;border:1px solid rgba(243,217,184,.6);padding:6px 12px;border-radius:999px;margin-bottom:18px;}
.mk .htext h2{color:#faf6ee;font-size:clamp(34px,4.6vw,56px);font-style:italic;margin-bottom:14px;}
.htext p{font-size:18px;opacity:.92;max-width:520px;margin:0 0 10px;}
.htext .hprice{font-weight:700;color:#f3d9b8;margin-bottom:22px;}
.mk .hbtn{display:inline-block;background:#faf6ee;color:#8e2f2a;font:700 14px Mulish,sans-serif;letter-spacing:.12em;text-transform:uppercase;padding:13px 26px;border-radius:4px;text-decoration:none;}
.mk .hbtn:hover{background:#fff;}
.mk .hbtn.ghost{background:transparent;color:#faf6ee;border:1.5px solid #faf6ee;}
.himg{height:100%;min-height:440px;display:flex;align-items:center;justify-content:center;padding:28px;background:radial-gradient(circle at 50% 50%,rgba(255,255,255,.14),rgba(255,255,255,0) 65%);}
.himg img{max-height:400px;max-width:100%;width:auto;border-radius:10px;box-shadow:0 18px 40px rgba(0,0,0,.35);}
.hdots{position:absolute;left:0;right:0;bottom:16px;display:flex;justify-content:center;gap:8px;}
.hdots span{width:9px;height:9px;border-radius:50%;background:rgba(250,246,238,.4);animation:mkdot 18s infinite;}
@keyframes mkfade{0%{opacity:0;visibility:visible}3%{opacity:1}30%{opacity:1}33.3%{opacity:0;visibility:visible}33.4%,100%{opacity:0;visibility:hidden}}
@keyframes mkdot{0%,33%{background:#faf6ee}33.4%,100%{background:rgba(250,246,238,.4)}}
@media (prefers-reduced-motion:reduce){.hslide,.hdots span{animation:none;}.hslide:first-child{opacity:1;visibility:visible;}}
.mk section.finds-sec{padding:48px 0;}
.finds{background:#f3e6e2;display:grid;grid-template-columns:170px 1fr;align-items:center;gap:20px;padding:30px 0 30px 30px;border-radius:4px;}
.mk .ftitle{font-size:clamp(30px,3.4vw,40px);font-weight:500;margin:0;color:#2b2420;}
.frow{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 30px 8px 0;scrollbar-width:thin;}
.mk .fcard{flex:0 0 280px;height:280px;position:relative;scroll-snap-align:start;overflow:hidden;border-radius:2px;text-decoration:none;}
.fcard img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s;}
.fcard:hover img{transform:scale(1.05);}
.fcap{position:absolute;left:0;right:0;bottom:0;background:rgba(43,36,32,.55);color:#faf6ee;padding:12px 18px;font-family:'Cormorant Garamond',serif;}
.fcap em{display:block;font-size:24px;font-weight:600;line-height:1.1;}
.fcap span{font-size:19px;}
.mk section.duo-sec{padding:12px 0 56px;}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.mk .dbanner{position:relative;display:block;height:340px;overflow:hidden;text-decoration:none;}
.dbanner img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s;}
.dbanner:hover img{transform:scale(1.04);}
.dbanner:after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(20,15,10,.75),rgba(20,15,10,0) 60%);}
.dtext{position:absolute;left:24px;bottom:22px;right:24px;z-index:1;color:#faf6ee;font-family:'Cormorant Garamond',serif;}
.dtext strong{display:block;font-size:clamp(24px,2.6vw,32px);letter-spacing:.03em;font-weight:600;}
.dtext em{display:block;font-size:22px;margin-bottom:10px;}
.dbtn{display:inline-block;background:#5a1f1c;color:#faf6ee;font:700 11px Mulish,sans-serif;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px;border-radius:999px;}
.mk section.promo{padding:56px 0;}
.promo-in{display:flex;justify-content:space-between;align-items:center;gap:30px;flex-wrap:wrap;}
.peyebrow{font:700 12px Mulish,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#f3d9b8;}
.mk .promo h2{color:#faf6ee;font-size:clamp(32px,4.4vw,52px);font-style:italic;margin:8px 0 10px;}
.promo p{max-width:560px;margin:0;opacity:.92;}
.pbtns{display:flex;gap:12px;flex-wrap:wrap;}
.mk section.story-sec{padding:64px 0;}
.vlist{display:grid;gap:14px;}
.vlist>div{background:#fff;border:1px solid #e2d6c3;border-left:4px solid #b5653f;border-radius:8px;padding:16px 20px;}
.vlist>div:nth-child(2){border-left-color:#23325a;}
.vlist>div:nth-child(3){border-left-color:#8e2f2a;}
.vlist .num{font:700 12px Mulish,sans-serif;color:#b5653f;letter-spacing:.14em;}
.mk .vlist h3{font-size:24px;margin:2px 0 4px;}
.vlist p{margin:0;font-size:15px;color:#6b5e55;}
.mk section.igband{background:#ece7e3;padding:44px 0 50px;}
.mk .ighandle{display:inline-flex;align-items:center;gap:8px;font:700 18px Mulish,sans-serif;color:#2b2420;text-decoration:none;}
.igband p{color:#6b5e55;margin:8px 0 22px;}
.iggrid{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;max-width:980px;margin:0 auto;}.iggrid a{flex:0 1 180px;}
.iggrid img{width:100%;aspect-ratio:1;object-fit:cover;display:block;border-radius:4px;}
.mk-footer2{background:#f3e6e2;color:#2b2420;padding:52px 0 26px;font-family:Mulish,sans-serif;}
.mk-footer2 .fcols{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;}
.mk-footer2 h4{font:700 16px Mulish,sans-serif;text-transform:uppercase;letter-spacing:.04em;color:#2b2420;margin:0 0 14px;}
.mk-footer2 a{display:block;color:#2b2420;text-decoration:none;font-size:14px;margin-bottom:9px;}
.mk-footer2 a:hover{color:#8e2f2a;}
.fbottom{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;margin-top:30px;padding-top:22px;border-top:1px solid #dccbc4;}
.ffollow{display:flex;align-items:center;gap:16px;font-weight:700;font-size:17px;}
.ffollow a{margin:0;}
.fstore{display:flex;flex-direction:column;font-size:14px;gap:2px;}
.fstore strong{font-size:17px;}
.mk-footer2 .small{margin-top:22px;font-size:13px;color:#6b5e55;}
.mk-float{display:flex;align-items:center;gap:8px;}
.mk .popt{font-size:.6em;font-weight:600;color:#6b5e55;text-transform:uppercase;letter-spacing:.06em;}
.mk .mrp{color:#8a7f76;font-weight:400;font-size:.82em;margin-left:6px;}
.pgal{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:12px;}
.pgal img{width:100%;height:auto;border-radius:10px;display:block;}
.mk .pdesc{font-size:16px;}
.mk .pdesc p{margin:0 0 .9em;}
.mk .pdesc ul{padding-left:20px;margin:0 0 1em;}
.mk .pdesc h3{font-size:22px;margin:1em 0 .4em;}
@media (max-width:860px){
  .hslide{grid-template-columns:1fr;min-height:0;}
  .himg{order:-1;min-height:0;padding:22px 20px 0;}
  .himg img{max-height:260px;}
  .htext{padding:22px 20px 46px;}
  .htext p{font-size:16px;}
  .finds{grid-template-columns:1fr;padding:22px 0 22px 20px;}
  .mk .fcard{flex-basis:220px;height:220px;}
  .duo{grid-template-columns:1fr;}
  .mk .dbanner{height:260px;}
  .mk-footer2 .fcols{grid-template-columns:1fr 1fr;}
}
@media (max-width:600px){
  .mk-head .in{padding:8px 16px;}
  .mk-logo{font-size:24px;gap:8px;}.mk-logo img{height:42px;}.mk-logo small{font-size:9px;}
  .mk-icons{gap:14px;}
  .mk-nav .nin{justify-content:flex-start;padding:0 16px;gap:20px;}
  .mk-nav a{font-size:14px;padding:9px 0;}
  .iggrid a{flex:0 1 calc(50% - 5px);}
  .mk-float span{display:none;}
  .mk-float{padding:12px !important;}
}
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#23325a"/><text x="32" y="45" font-family="Georgia,serif" font-size="40" font-weight="700" text-anchor="middle" fill="#faf6ee">M</text></svg>"""

if os.path.exists(OUT):
    keep_images = os.path.exists(f"{OUT}/images")
else:
    keep_images = False
os.makedirs(f"{OUT}/images", exist_ok=True)
with open(f"{OUT}/style.css", "w") as f:
    f.write("\n".join(l for l in open(CSS_SRC).read().split("*/", 1)[1].lstrip().splitlines() if not l.startswith("@import")) + HEADER_CSS)
with open(f"{OUT}/images/README.txt", "w") as f:
    f.write("Put product photos here, named by product code, e.g. MK-BS-001.jpg\n")

NAV = [("index", "Home"), ("shop", "Shop All")] + [(s if s in PAGE_CATS else f"shop.html#{s}", n) for s, n, _ in CATS] + [("about", "Our Story"), ("contact", "Contact")]
for slug, _, body, title, desc, extra_head, og_img in PAGES:
    nav = "".join(f'<a class="{"on" if s == slug or (s in CAT_SLUG_PREFIX and slug.startswith(CAT_SLUG_PREFIX[s])) else ""}" href="{s if "#" in s else s + ".html"}">{n}</a>' for s, n in NAV)
    url = DOMAIN + ("/" if slug == "index" else f"/{slug}.html")
    doc = f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-src https://www.google.com; object-src 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="format-detection" content="telephone=no">
<title>{title}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="logo.png">
<meta property="og:image" content="{og_img}">
<meta name="robots" content="index,follow,max-image-preview:large">
{extra_head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Mulish:wght@400;600;700&display=swap">
<link rel="preload" as="image" href="logo-120.webp">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="mk-bar">Handmade in India. Free shipping across India (bedsheets above Rs 1,000). Order easily on <a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a>.</div>
<header class="mk-head"><div class="in"><a class="mk-logo" href="index.html"><img src="logo-120.webp" alt="Mookmati, The Silent Earth Studio" width="46" height="60"><span>Mookmati<small>The Silent Earth Studio</small></span></a><div class="mk-icons"><a href="contact.html" title="Visit our store" aria-label="Visit our store">{_ico("pin")}</a><a href="{IG_URL}" target="_blank" rel="noopener" title="Instagram" aria-label="Instagram">{_ico("ig")}</a><a href="{wa()}" target="_blank" rel="noopener" title="WhatsApp" aria-label="WhatsApp">{_ico("wa")}</a><a href="shop.html" title="Shop" aria-label="Shop">{_ico("bag")}</a></div></div><nav class="mk-nav" aria-label="Main"><div class="nin">{nav}</div></nav></header>
<main class="mk">{body}</main>
{footer}
</body>
</html>
"""
    with open(f"{OUT}/{slug}.html", "w") as f:
        f.write(doc)

# 404 page and sitemap
src = open(f"{OUT}/index.html").read()
start, end = src.index('<main class="mk">'), src.index("</main>")
nf = ('<main class="mk"><section class="pagehead print"><div class="wrap"><h1>Page not found</h1>'
      '<p>The page you are looking for has moved.</p></div></section>'
      '<section><div class="wrap" style="text-align:center;"><a class="btn btn-dark" href="index.html">Go to the home page</a></div></section>')
with open(f"{OUT}/404.html", "w") as f:
    out = src[:start] + nf + src[end:]
    out = re.sub(r'(href|src)="(?!https?:|mailto:|/|#)', r'\1="/', out)
    out = out.replace('<link rel="canonical" href="https://mookmati.in/">\n', '')
    out = re.sub(r"<title>.*?</title>", "<title>Page not found | Mookmati</title>", out, count=1)
    out = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", out, flags=re.S)
    out = out.replace('content="index,follow,max-image-preview:large"', 'content="noindex"')
    f.write(out)
with open(f"{OUT}/sitemap.xml", "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            "".join(f"  <url><loc>{DOMAIN}{'/' if s == 'index' else '/' + s + '.html'}</loc><lastmod>{TODAY}</lastmod></url>\n" for s, *_ in PAGES) +
            "</urlset>\n")
# Google Merchant Center product feed (RSS 2.0 with g: namespace)
from xml.sax.saxutils import escape as _x
_items = []
for _cat, _plist in CATALOG.items():
    if _cat.startswith("_"):
        continue
    for _p in _plist:
        if not _p.get("price"):
            continue
        _img = next((f"images/{_p['code']}.{e}" for e in ("jpg", "webp") if os.path.exists(f"{OUT}/images/{_p['code']}.{e}")), "logo.png")
        _items.append(f"""  <item>
    <g:id>{_x(_p['code'])}</g:id>
    <g:title>{_x(_p['title'])}</g:title>
    <g:description>{_x(_p['desc'])} {(BS_SHIP + '.') if _cat == 'bedsheets' else 'Free shipping across India.'} Order on WhatsApp +91 94566 01984.</g:description>
    <g:link>{SITE}/{_p['slug']}.html</g:link>
    <g:image_link>{SITE}/{_img}</g:image_link>
    <g:availability>in_stock</g:availability>
    <g:price>{_num(_p['price'])}.00 INR</g:price>
    <g:brand>Mookmati</g:brand>
    <g:condition>new</g:condition>
    <g:identifier_exists>no</g:identifier_exists>
    <g:google_product_category>{_x(GPC.get(_cat, "Home & Garden"))}</g:google_product_category>
    <g:product_type>{_x(_cat.replace('-', ' ').title())}</g:product_type>
""" + ("""    <g:material>Cotton</g:material>
    <g:size>""" + _x(_size_of(_p.get("title"))) + """</g:size>
""" if _cat == "bedsheets" else "") + ("" if (_cat == "bedsheets" and not _bs_free(_p["price"])) else f"""    <g:shipping>
      <g:country>IN</g:country>
      <g:service>Standard</g:service>
      <g:price>0.00 INR</g:price>
    </g:shipping>
""") + f"""  </item>
""")
with open(f"{OUT}/feed.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n<channel>\n'
            f"  <title>Mookmati products</title>\n  <link>{SITE}/</link>\n  <description>Handmade products from Mookmati, The Silent Earth Studio</description>\n"
            + "".join(_items) + "</channel>\n</rss>\n")

with open(f"{OUT}/robots.txt", "w") as f:
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Applebot", "Applebot-Extended", "DuckDuckBot", "YandexBot"]
    f.write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
with open(f"{OUT}/llms.txt", "w") as f:
    f.write(LLMS)
print("built")
