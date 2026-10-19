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
_bs_prices = sorted({_num(p["price"]) for p in CATALOG.get("bedsheets", []) if p["price"]})
def _inr(n): return f"{n:,}"
PRICE_FROM = (f"from \u20b9{_inr(_bs_prices[0])}" if len(_bs_prices) > 1 else f"\u20b9{_inr(_bs_prices[0])}") if _bs_prices else ""
PRICE_FROM_HTML = PRICE_FROM.replace("\u20b9", "&#8377;")

def product_card(code, name, note, price, idx=0):
    shade = ["", " clay", " madder"][idx % 3]
    photo = None
    for ext in ("png", "jpeg", "jpg", "webp"):
        if os.path.exists(f"{OUT}/images/{code}.{ext}"):
            photo = f"images/{code}.{ext}"
    img = (f'<div class="pimg has-img"><img src="{photo}" alt="{esc(name)}" decoding="async" width="337" height="421"></div>'
           if photo else f'<div class="pimg print{shade}" aria-hidden="true"></div>')
    price_txt = (f"&#8377; {price} <span class=\"pship\">Free shipping in India</span>") if price else "Price on request"
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
    f'        <a class="cat" href="{"bedsheets.html" if s == "bedsheets" else "shop.html#" + s}"><img src="images/categories/{s}.webp" alt="{n}" loading="lazy" decoding="async" width="440" height="330"><span class="name">{n}</span>'
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
home = f"""
  <section class="hero print">
    <div class="wrap">
      <img src="logo-360.webp" alt="Mookmati, The Silent Earth Studio" fetchpriority="high" width="150" height="197" style="width:150px;height:auto;border-radius:12px;margin:0 auto 22px;display:block;box-shadow:0 8px 24px rgba(0,0,0,.25);">
      <h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Mookmati, The Silent Earth Studio</h1>
      <p class="tag">The silent earth, shaped by hand.</p>
      <p class="sub">Textiles, sarees, jewellery and crafts made slowly by Indian artisans, and guided by the path of non-violence.</p>
      <div class="btns">
        <a class="btn btn-clay" href="shop.html">Shop the collection</a>
        <a class="btn btn-line" href="{wa('Hello Mookmati, I would like to know more about your products.')}" target="_blank" rel="noopener">Chat on WhatsApp</a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap split">
      <div class="products" style="grid-template-columns:1fr 1fr;width:100%;">{product_card(*bs[0])}{product_card(*bs[1], idx=1)}
      </div>
      <div>
        <span class="eyebrow">Our first collection</span>
        <h2>Hand block-printed bedsheets</h2>
        <p>Our journey begins with pure cotton bedsheets, printed by hand in Rajasthan. Prices start {PRICE_FROM_HTML.replace("from ","at ")}, with free shipping across India.</p>
        <p>Each sheet is printed one wooden block at a time. Small variations in the print are the mark of a human hand, not a flaw.</p>
        <div class="btns" style="justify-content:flex-start;">
          <a class="btn btn-dark" href="shop.html#bedsheets">See all bedsheets</a>
        </div>
      </div>
    </div>
  </section>

  <section class="tint">
    <div class="wrap">
      <div class="center">
        <span class="eyebrow">Shop by category</span>
        <h2>Made by hand, for everyday life</h2>
        <p>Bedsheets are available now. More collections are on their way.</p>
      </div>
      <div class="cats">
{photo_tiles}        <a class="cat" href="shop.html"><img src="images/MK-BS-002.webp" alt="Mookmati hand block-printed bedsheet" loading="lazy" decoding="async"><span class="name">View all</span><span class="go">Full collection</span></a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap split">
      <div>
        <span class="eyebrow">Our story</span>
        <h2>Named after the silent earth</h2>
        <p>Mookmati takes its name from <em>Mookmati</em>, the epic by Acharya Vidyasagar Ji. At its heart is humble clay, shaped through patience into something useful and beautiful.</p>
        <p>We choose what we sell in the same spirit. Every piece is made by hand. Every choice starts with one question: does this cause harm?</p>
        <a class="btn btn-dark" href="about.html">Read our story</a>
      </div>
      <div>
        <p class="quote">Ahimsa is not only what we avoid. It is how we choose to make things.</p>
        <p>Non-violence, as taught by Acharya Vidyasagar Ji, guides our brand. It shapes the materials we pick, the artisans we work with, and the pace at which we work.</p>
      </div>
    </div>
  </section>

  <section class="tint">
    <div class="wrap">
      <div class="center">
        <span class="eyebrow">Why Mookmati</span>
        <h2>What we stand for</h2>
      </div>
      <div class="grid3">
        <div class="vcard"><span class="num">01</span><h3>Made by hand</h3><p>Every piece passes through an artisan's hands. Small variations are the mark of real craft.</p></div>
        <div class="vcard"><span class="num">02</span><h3>Gentle by choice</h3><p>We favour natural materials and dyes wherever the craft allows.</p></div>
        <div class="vcard"><span class="num">03</span><h3>Fair to makers</h3><p>We work directly with artisans so more of every sale reaches the people who made it.</p></div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="center">
        <span class="eyebrow">How to order</span>
        <h2>Simple, personal, direct</h2>
      </div>
      <div class="steps">
        <div class="step"><h3>Pick a piece</h3><p>Browse the shop and tap "Order on WhatsApp" on any product.</p></div>
        <div class="step"><h3>Chat with us</h3><p>We confirm availability, price and delivery time on WhatsApp.</p></div>
        <div class="step"><h3>Pay and receive</h3><p>Complete payment and we ship it to your door.</p></div>
      </div>
    </div>
  </section>

  <section class="print clay">
    <div class="wrap" style="text-align:center;">
      <span class="eyebrow" style="color:#fbe3cf;">Follow us</span>
      <h2 style="color:#faf6ee;font-size:clamp(30px,4.5vw,44px);">@{IG} on Instagram</h2>
      <p style="max-width:520px;margin:0 auto 26px;">New arrivals, artisan stories and behind-the-scenes from our studio.</p>
      <a class="btn btn-line" href="{IG_URL}" target="_blank" rel="noopener">Follow @{IG}</a>
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
    body = (f'<div class="products">{"".join(product_card(*p, idx=i + j) for j, p in enumerate(PRODUCTS[s]))}\n      </div>'
            if live(s) else coming_soon(n))
    shop += f"""
    <div class="shopcat" id="{s}">
      <h2>{n}</h2>
      <p class="lead">{lead}{' <a href="bedsheets.html">About our bedsheets</a>' if s == "bedsheets" else ''}</p>
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
            <span style="display:block;font-size:12px;color:var(--muted);">Photo: <a href="https://commons.wikimedia.org/wiki/File:0521_acaaraya.jpg" target="_blank" rel="noopener">Agniban.com via Wikimedia Commons</a>, public domain, cropped.</span>
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
      <p>We are starting small, with hand block-printed bedsheets from Rajasthan. Sarees, handloom, jewellery, home decor, serveware and handicrafts will follow as we find artisans whose work we are proud to share.</p>
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
        <div class="ccard"><h3>Visit our store</h3><p>GF193, Gaur City Center,<br>Noida Extension</p><a class="btn btn-clay" href="https://www.google.com/maps/search/?api=1&amp;query=Gaur+City+Center+Noida+Extension" target="_blank" rel="noopener">Get directions</a></div>
        <div class="ccard"><h3>Instagram</h3><p>New arrivals and artisan stories.</p><a class="btn btn-dark" href="{IG_URL}" target="_blank" rel="noopener">@{IG}</a></div>
      </div>
    </div>
  </section>
  <section class="tint">
    <div class="wrap narrow">
      <div class="center" style="margin-bottom:20px;"><h2>Frequently asked questions</h2></div>
      <details><summary>How do I place an order?</summary><p>Tap "Order on WhatsApp" on any product. We confirm price, stock and delivery time in the chat, then share payment details.</p></details>
      <details><summary>How can I pay?</summary><p>We share payment options on WhatsApp when we confirm your order.</p></details>
      <details><summary>How long does delivery take?</summary><p>We tell you the expected delivery date on WhatsApp before you pay. See our <a href="shipping.html">Shipping Policy</a> for details.</p></details>
      <details><summary>Can I return or exchange a product?</summary><p>Yes. See our <a href="returns.html">Returns and Exchanges</a> policy.</p></details>
      <details><summary>Why does my product look slightly different from the photo?</summary><p>Handmade products vary a little from piece to piece. Colours may also look different on different screens. These variations are part of the craft and are not defects.</p></details>
    </div>
  </section>
"""

def policy(title, intro, body):
    return f"""
  <section class="pagehead print">
    <div class="wrap"><h1>{title}</h1><p>{intro}</p></div>
  </section>
  <section>
    <div class="wrap narrow prose">
      <p class="updated">Last updated: 10 October 2026</p>
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
      <p>Shipping is free on all orders within India. International shipping is charged extra, and we confirm the exact charge on WhatsApp before you pay. There are no hidden costs.</p>
      <h2>Tracking</h2>
      <p>We share a tracking link on WhatsApp once your order is dispatched.</p>
      <h2>Damaged in transit</h2>
      <p>If your parcel arrives damaged, please record an unboxing video and message us within 48 hours. See our <a href="returns.html">Returns and Exchanges</a> policy.</p>
""")

returns = policy("Returns and Exchanges", "Our promise if something is not right.", f"""
      <div class="box"><strong>In short:</strong> message us on WhatsApp within 7 days of delivery. Unused items in original condition can be exchanged or returned. Damaged or wrong items are replaced at no cost to you.</div>
      <h2>Eligibility</h2>
      <ul>
        <li>Request a return or exchange within 7 days of delivery.</li>
        <li>The item must be unused, unwashed and in its original packaging with tags.</li>
        <li>Custom or made-to-order pieces cannot be returned unless they arrive damaged or incorrect.</li>
      </ul>
      <h2>Damaged, defective or wrong items</h2>
      <p>Please share photos and an unboxing video on WhatsApp within 48 hours of delivery. We will arrange a replacement or full refund at no extra cost.</p>
      <h2>About handmade variations</h2>
      <p>Handmade products show small differences in print, weave, colour and finish. These are signs of handcraft and are not treated as defects.</p>
      <h2>How to start a return</h2>
      <ol>
        <li>Message us on <a href="{wa('Hello Mookmati, I would like to return or exchange an order.')}" target="_blank" rel="noopener">WhatsApp</a> with your order details and photos.</li>
        <li>We confirm eligibility and share the return address or arrange a pickup.</li>
        <li>Once we receive and check the item, we process your exchange or refund.</li>
      </ol>
      <h2>Refunds</h2>
      <p>Approved refunds are paid to your original payment method within 7 working days of our receiving the returned item.</p>
""")

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

footer = f"""<footer class="mk mk-footer">
  <div class="wrap">
    <div class="fgrid">
      <div>
        <img src="logo-360.webp" alt="Mookmati logo" loading="lazy" width="68" height="90" style="height:90px;width:auto;border-radius:8px;margin-bottom:12px;display:block;">
        <span class="brand">Mookmati</span>
        <p style="opacity:.85;">Handmade in India. Guided by non-violence.</p>
        <a href="{IG_URL}" target="_blank" rel="noopener">Instagram: @{IG}</a>
        <a href="{wa()}" target="_blank" rel="noopener">WhatsApp: +91 94566 01984</a>
      </div>
      <div>
        <h4>Shop</h4>
""" + "".join(f'        <a href="{"bedsheets.html" if s == "bedsheets" else "shop.html#" + s}">{n}</a>\n' for s, n, _ in CATS) + """      </div>
      <div>
        <h4>Help</h4>
        <a href="contact.html">Contact and FAQ</a>
        <a href="shipping.html">Shipping Policy</a>
        <a href="returns.html">Returns and Exchanges</a>
      </div>
      <div>
        <h4>About</h4>
        <a href="about.html">Our story</a>
        <a href="privacy.html">Privacy Policy</a>
        <a href="terms.html">Terms of Use</a>
        <a href="credits.html">Photo Credits</a>
      </div>
    </div>
    <div class="small">&copy; 2026 Mookmati. All rights reserved.</div>
  </div>
</footer>
<a class="mk-float" href=\"""" + wa("Hello Mookmati!") + """\" target="_blank" rel="noopener">WhatsApp us</a>"""

import json
SITE = DOMAIN
def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

ORG = {
  "@context": "https://schema.org", "@type": "Store", "@id": SITE + "/#store",
  "name": "Mookmati", "alternateName": "Mookmati, The Silent Earth Studio",
  "url": SITE + "/", "logo": SITE + "/logo.png", "image": SITE + "/logo.png",
  "description": "Mookmati, The Silent Earth Studio, sells hand block-printed cotton bedsheets and handmade Indian goods guided by ahimsa (non-violence). Orders on WhatsApp, free shipping across India.",
  "telephone": "+91-9456601984",
  "address": {"@type": "PostalAddress", "streetAddress": "GF193, Gaur City Center", "addressLocality": "Greater Noida West (Noida Extension)", "addressRegion": "Uttar Pradesh", "addressCountry": "IN"},
  "areaServed": "IN", "currenciesAccepted": "INR",
  "sameAs": [IG_URL],
  "contactPoint": {"@type": "ContactPoint", "telephone": "+91-9456601984", "contactType": "sales", "availableLanguage": ["en", "hi"]},
}

PDETAIL = {p["code"]: {"title": p["title"], "lead": p["lead"], "points": p["points"], "desc": p["desc"]}
           for cat, items in CATALOG.items() if not cat.startswith("_") for p in items}

def product_ld(code, name, price, slug, img):
    d = PDETAIL[code]
    return {
      "@context": "https://schema.org", "@type": "Product", "sku": code, "name": name,
      "description": d["desc"], "image": [SITE + "/" + img], "brand": {"@type": "Brand", "name": "Mookmati"},
      "material": "Cotton", "size": "108 x 108 inches", "category": "Home & Garden > Linens & Bedding > Bedding > Bed Sheets",
      "countryOfOrigin": "IN",
      "offers": {"@type": "Offer", "url": f"{SITE}/{slug}.html", "price": price.replace(",", ""), "priceCurrency": "INR",
                 "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
                 "seller": {"@id": SITE + "/#store"},
                 "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "INR"},
                                     "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "IN"}},
                 "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "IN",
                                             "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                                             "merchantReturnDays": 7, "returnMethod": "https://schema.org/ReturnByMail"}},
    }

def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

BS_FAQ = [
 ("What size are Mookmati bedsheets?", "Our bedsheets are 108 x 108 inches (king, king plus or super king). They fit king and super king beds, and drape generously over queen beds."),
 ("What are the bedsheets made of?", "They are made of 100% pure cotton, which is soft, breathable and cool on warm nights."),
 ("What is hand block printing?", "Artisans press carved wooden blocks dipped in dye onto the cloth, one impression at a time. Small variations in the print are the mark of handwork, not a flaw."),
 ("How much do the bedsheets cost?", f"Our bedsheets are priced {PRICE_FROM}, with free shipping anywhere in India. International shipping is available at an extra charge."),
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
      <p>Pure cotton bedsheets from Rajasthan, printed by hand and sized generously at 108 x 108 inches. Priced {PRICE_FROM_HTML}, with free shipping across India.</p>
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
        <li><strong>Large size:</strong> 108 x 108 inches, which fits king and super king beds with room to tuck in.</li>
        <li><strong>Gentle choices:</strong> natural dyes wherever the craft allows, and no silk. Our work is guided by ahimsa, the path of non-violence taught by Acharya Shri Vidyasagar Ji Maharaj.</li>
        <li><strong>Fair price:</strong> {PRICE_FROM_HTML}, with free shipping across India.</li>
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

# Individual product pages
PRODUCT_PAGES = []
for code, name, note, price in PRODUCTS["bedsheets"]:
    d = PDETAIL[code]; slug = PRODUCT_SLUG[code]; img = product_img(code)
    msg = f"Hello Mookmati, I would like to order the {name} (code {code})."
    body = f"""
  <section>
    <div class="wrap">
      <p style="font-size:14px;color:var(--muted);margin-bottom:24px;"><a href="index.html">Home</a> / <a href="bedsheets.html">Bedsheets</a> / {name}</p>
      <div class="split" style="align-items:start;">
        <div><img src="{img}" alt="{esc(d['title'])}" fetchpriority="high" style="width:100%;height:auto;border-radius:14px;display:block;"></div>
        <div>
          <span class="eyebrow">{code}</span>
          <h1 style="font-size:clamp(32px,4.5vw,44px);">{name}</h1>
          <p style="font-size:19px;">{d['lead']}</p>
          <p class="pprice" style="font-size:26px;">&#8377; {price}<span class="pship" style="font-size:14px;">Free shipping across India. International shipping charged extra.</span></p>
          <ul class="ticks" style="list-style:none;padding:0;">""" + "".join(f'<li style="padding-left:24px;position:relative;margin-bottom:8px;"><span style="position:absolute;left:0;top:9px;width:10px;height:10px;border-radius:50%;background:var(--clay);"></span>{x}</li>' for x in d["points"]) + f"""</ul>
          <div class="btns" style="justify-content:flex-start;margin-top:18px;">
            <a class="btn btn-wa" href="{wa(msg)}" target="_blank" rel="noopener">Order on WhatsApp</a>
            <a class="btn btn-dark" href="{IG_URL}" target="_blank" rel="noopener">See it on Instagram</a>
          </div>
          <p style="font-size:14px;color:var(--muted);margin-top:18px;">Prefer to see it in person? Visit our store at GF193, Gaur City Center, Noida Extension. See our <a href="shipping.html">Shipping</a> and <a href="returns.html">Returns</a> policies.</p>
        </div>
      </div>
    </div>
  </section>
"""
    head = ld(product_ld(code, name, price, slug, img)) + "\n" + ld(crumbs([("Home", "/"), ("Bedsheets", "/bedsheets.html"), (name, f"/{slug}.html")]))
    PRODUCT_PAGES.append((slug, None, body, f"{d['title']} | Mookmati", d["desc"] + f" \u20b9{price}, free shipping in India.", head, SITE + "/" + img))

SCHEMA = {
  "index": ld(ORG) + "\n" + ld({"@context": "https://schema.org", "@type": "WebSite", "name": "Mookmati", "url": SITE + "/"}),
  "contact": ld(ORG),
  "about": ld(ORG),
  "bedsheets": ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Hand block-printed cotton bedsheets",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{PRODUCT_SLUG[c]}.html", "name": n} for i, (c, n, _, _) in enumerate(PRODUCTS["bedsheets"])]})
               + "\n" + ld(faq_ld) + "\n" + ld(crumbs([("Home", "/"), ("Bedsheets", "/bedsheets.html")])),
}

LLMS = """# Mookmati, The Silent Earth Studio

> Mookmati (mookmati.in) is an Indian brand selling handmade home textiles and crafts guided by ahimsa (non-violence), inspired by Acharya Shri Vidyasagar Ji Maharaj and his epic Mookmati. Current products are hand block-printed 100% cotton bedsheets from Rajasthan, 108 x 108 inches, priced """ + PRICE_FROM.replace("\u20b9","Rs ") + """ with free shipping across India. Orders are placed on WhatsApp (+91 94566 01984) or Instagram (@mookmatistudio). Store: GF193, Gaur City Center, Noida Extension (Greater Noida West), Uttar Pradesh, India.

## Products
- [Hand block-printed cotton bedsheets](https://mookmati.in/bedsheets.html): category overview, sizes, care and FAQs
""" + "".join(f"- [{p['name']}](https://mookmati.in/{p['slug']}.html): {p['desc']} Rs {p['price']}\n" for p in CATALOG["bedsheets"]) + """- [All products](https://mookmati.in/shop.html): sarees, handloom, jewellery, home decor, serveware and handicrafts coming soon

## About and policies
- [About Mookmati](https://mookmati.in/about.html)
- [Contact and FAQ](https://mookmati.in/contact.html)
- [Shipping](https://mookmati.in/shipping.html): free shipping in India, international shipping charged extra
- [Returns and exchanges](https://mookmati.in/returns.html): 7-day returns on unused items
"""

PAGES = [
    ("index", "Home", home, "Mookmati | Hand Block-Printed Cotton Bedsheets, Handmade in India",
     "Shop hand block-printed 100% cotton bedsheets from Rajasthan, king size 108 x 108 inches, " + PRICE_FROM + " with free shipping across India. Handmade goods guided by ahimsa. Order on WhatsApp."),
    ("bedsheets", None, bedsheets_page, "Hand Block-Printed Cotton Bedsheets, King Size 108 x 108 | Mookmati",
     "Pure cotton hand block-printed bedsheets from Rajasthan, 108 x 108 inches, " + PRICE_FROM + " with free shipping across India. Natural dyes, no silk. Order on WhatsApp or visit our Noida Extension store."),
    ("shop", "Shop", shop, "Shop | Mookmati",
     "Shop handmade cotton bedsheets, with sarees, handloom, jewellery, home decor, serveware and handicrafts coming soon. Order on WhatsApp, free shipping in India."),
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
.mk-head{background:#faf6ee;border-bottom:1px solid #e2d6c3;font-family:Mulish,sans-serif;}
.mk-head .in{max-width:1180px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;}
.mk-logo{font:600 30px 'Cormorant Garamond',serif;color:#23325a;text-decoration:none;line-height:1;display:flex;align-items:center;gap:12px;}
.mk-logo img{height:60px;width:auto;border-radius:6px;display:block;}
.mk-logo small{display:block;font:600 11px Mulish,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#b5653f;margin-top:4px;}
.mk .pship{display:block;font-size:12px;font-weight:600;color:#1f7a4d;margin-top:2px;}
.mk-nav{display:flex;gap:18px;flex-wrap:wrap;}
.mk-nav a{color:#2b2420;text-decoration:none;font-weight:600;font-size:15px;}
.mk-nav a:hover,.mk-nav a.on{color:#b5653f;}
@media (max-width:480px){.mk .cat{padding:16px;}.mk .cat .name{font-size:22px;}}
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

NAV = [("index", "Home"), ("shop", "Shop"), ("about", "About"), ("contact", "Contact")]
for slug, _, body, title, desc, extra_head, og_img in PAGES:
    nav = "".join(f'<a class="{"on" if s == slug else ""}" href="{s}.html">{n}</a>' for s, n in NAV)
    url = DOMAIN + ("/" if slug == "index" else f"/{slug}.html")
    doc = f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests">
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
<div class="mk-bar">Handmade in India. Order easily on <a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a>.</div>
<header class="mk-head"><div class="in"><a class="mk-logo" href="index.html"><img src="logo-120.webp" alt="Mookmati, The Silent Earth Studio" width="46" height="60"><span>Mookmati<small>The Silent Earth Studio</small></span></a><nav class="mk-nav">{nav}</nav></div></header>
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
GPC = {"bedsheets": "Home & Garden > Linens & Bedding > Bedding > Bed Sheets"}
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
    <g:description>{_x(_p['desc'])} Free shipping across India. Order on WhatsApp +91 94566 01984.</g:description>
    <g:link>{SITE}/{_p['slug']}.html</g:link>
    <g:image_link>{SITE}/{_img}</g:image_link>
    <g:availability>in_stock</g:availability>
    <g:price>{_num(_p['price'])}.00 INR</g:price>
    <g:brand>Mookmati</g:brand>
    <g:condition>new</g:condition>
    <g:identifier_exists>no</g:identifier_exists>
    <g:google_product_category>{_x(GPC.get(_cat, "Home & Garden"))}</g:google_product_category>
    <g:product_type>{_x(_cat.replace('-', ' ').title())}</g:product_type>
    <g:material>Cotton</g:material>
    <g:size>108 x 108 inches</g:size>
    <g:shipping>
      <g:country>IN</g:country>
      <g:service>Standard</g:service>
      <g:price>0.00 INR</g:price>
    </g:shipping>
  </item>
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
