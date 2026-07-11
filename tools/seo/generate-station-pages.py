#!/usr/bin/env python3
import json, math, re, urllib.request
from pathlib import Path
from html import escape
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
TODAY = date.today().isoformat()
APP_ID = "6760085664"
STATE = "ca"
STATE_NAME = "California"

PILOT_IDS = [
    # San Diego / SoCal harbors and beaches
    "9410170", "9410230", "9410580", "9410583", "9410660",
    "9410738", "9410840",
    # Ventura / Santa Barbara / Channel Islands / Central Coast
    "9410962", "9410971", "9411065", "9411189", "9411270",
    "9411340", "9411399", "9412110",
    # Monterey / Bay Area / NorCal (at least 5 NorCal)
    "9413375", "9413450", "9413616", "9414290", "9414523",
    "9414750", "9415020", "9416841", "9418767", "9419750",
]

REGION_RULES = [
    (33.3, "San Diego coast"),
    (34.15, "Los Angeles and Orange County coast"),
    (34.75, "Ventura, Santa Barbara, and the Channel Islands"),
    (36.2, "Central Coast"),
    (37.2, "Monterey Bay"),
    (38.7, "San Francisco Bay and Marin"),
    (90, "Northern California coast"),
]

SURF_NAMES = ("beach", "pier", "cove", "island", "santa monica", "santa barbara", "la jolla", "rincon", "gaviota", "ventura", "monterey", "moss landing", "point reyes", "arena cove", "north spit", "crescent city", "san diego", "san luis", "carmel")
HARBOR_NAMES = ("harbor", "port", "bay", "marina", "landing", "terminal", "alameda", "redwood", "richmond", "martinez", "chicago", "santa barbara", "ventura", "san diego", "los angeles", "san francisco")
FISH_NAMES = SURF_NAMES + HARBOR_NAMES + ("river", "slough", "catalina", "santa cruz", "santa rosa", "newport", "balboa")

def slugify(name, station_id):
    s = name.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{s}-{station_id}"

def norm_name(name):
    # NOAA tide-prediction endpoint uses some all-caps principal station labels.
    parts = []
    for part in name.split(' '):
        token = part.strip('(),')
        if len(token) > 1 and token.isupper():
            parts.append(part.replace(token, token.title()))
        else:
            parts.append(part)
    return ' '.join(parts).replace("Nwlon", "NWLON")

def region_for(lat):
    for max_lat, label in REGION_RULES:
        if lat <= max_lat:
            return label
    return STATE_NAME

def distance(a,b):
    # haversine miles
    R = 3958.8
    lat1,lon1 = math.radians(a['lat']), math.radians(a['lng'])
    lat2,lon2 = math.radians(b['lat']), math.radians(b['lng'])
    dlat,dlon = lat2-lat1,lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(h))

def app_url(station_id):
    return f"https://apps.apple.com/app/apple-store/id{APP_ID}?pt=119725640&ct=seo-station-{station_id}&mt=8"

def station_type(s):
    aff = (s.get('affiliations') or '').strip()
    if aff:
        return aff
    return "NOAA tide prediction station"

def use_blocks(name):
    n = name.lower()
    surf = any(x in n for x in SURF_NAMES) and not any(x in n for x in ("river", "slough", "lake", "martinez", "port chicago", "west sacramento", "redwood city"))
    harbor = any(x in n for x in HARBOR_NAMES)
    fish = any(x in n for x in FISH_NAMES)
    return surf, fish, harbor

url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions&units=english"
with urllib.request.urlopen(url, timeout=30) as r:
    data = json.load(r)
all_ca = []
for s in data['stations']:
    if s.get('state') == 'CA' and s.get('lat') is not None and s.get('lng') is not None:
        s = dict(s)
        s['name'] = norm_name(s['name'])
        s['slug'] = slugify(s['name'], s['id'])
        all_ca.append(s)
by_id = {s['id']: s for s in all_ca}
stations = [by_id[i] for i in PILOT_IDS]

css = '''
.station-hero{padding:72px 0 44px;background:radial-gradient(820px 460px at 82% 8%,rgba(61,210,232,.13),transparent 60%),var(--m-base)}
.station-kicker{color:var(--m-accent);font-family:var(--f-round);font-size:.8rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px}.station-hero h1{font-size:clamp(2.2rem,5vw,4rem);max-width:850px}.station-lede{max-width:760px;color:var(--m-text-2);font-size:1.15rem;margin-top:18px}.station-grid{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(280px,.8fr);gap:28px;padding:34px 0 72px}.station-card{background:linear-gradient(180deg,var(--m-card),var(--m-card-2));border:1px solid var(--m-hairline);border-radius:var(--r-card);padding:26px}.station-card h2,.station-card h3{margin-bottom:12px}.station-card p{color:var(--m-text-2);margin:0 0 14px}.fact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:8px}.fact{border:1px solid var(--m-hairline);border-radius:14px;padding:14px;background:rgba(255,255,255,.03)}.fact b{display:block;font-family:var(--f-round);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--m-text-3);margin-bottom:4px}.fact span{color:var(--m-text)}.cta-panel{position:sticky;top:84px}.app-cta{display:inline-flex;align-items:center;justify-content:center;width:100%;padding:14px 18px;border-radius:var(--r-cta);background:var(--m-accent);color:var(--deep-navy);font-weight:800;text-decoration:none;margin:8px 0 14px}.nearby-list{list-style:none;margin:0;padding:0}.nearby-list li{border-top:1px solid var(--m-hairline);padding:11px 0}.nearby-list a{color:var(--m-text);text-decoration:none}.nearby-list small{color:var(--m-text-3)}.notice{border-left:4px solid var(--gold);padding:13px 15px;background:rgba(242,192,64,.08);border-radius:0 14px 14px 0;color:var(--m-text-2)}.crumbs{font-size:.88rem;color:var(--m-text-3);margin-bottom:18px}.crumbs a{color:var(--m-text-2);text-decoration:none}@media(max-width:820px){.station-grid{grid-template-columns:1fr}.cta-panel{position:static}.fact-grid{grid-template-columns:1fr}}
'''

def nav():
    return '<nav class="site"><div class="wrap"><a class="brand" href="/">RipCat</a><div class="nav-links"><a href="/#features">Features</a><a href="/pro.html">Pro</a><a class="nav-cta" href="https://apps.apple.com/app/apple-store/id6760085664?pt=119725640&ct=site-nav&mt=8">Get the app</a></div></div></nav>'

def footer():
    return '<footer><div class="wrap"><p>Made in Santa Barbara by a surfer, his daughter, and their cat. NOAA/NWS/NDBC data. Predictions and forecasts are not navigation advice.</p></div></footer>'

station_dir = ROOT / 'tides' / STATE
station_dir.mkdir(parents=True, exist_ok=True)

# index
cards=[]
for s in stations:
    cards.append(f'''<article class="station-card"><h2><a href="/tides/ca/{s['slug']}/">{escape(s['name'])}</a></h2><p>{escape(region_for(float(s['lat'])))} · NOAA station {s['id']}</p></article>''')
index_html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>California NOAA Tide Stations | RipCat</title><meta name="description" content="Preview pilot pages for California NOAA tide stations in RipCat: Santa Barbara, Ventura, San Diego, San Francisco, Monterey, and more."><meta name="apple-itunes-app" content="app-id={APP_ID}"><link rel="canonical" href="https://ripcat.dev/tides/ca/"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="/site.css"><style>{css}</style></head><body>{nav()}<main><section class="station-hero"><div class="wrap"><div class="station-kicker">NOAA tide stations</div><h1>California tide charts in RipCat</h1><p class="station-lede">A first pilot set of station pages for California. These pages do not publish live tide heights; they point people to RipCat for live NOAA predictions, favorites, buoys, and marine advisories.</p></div></section><section class="wrap station-grid"><div>{''.join(cards)}</div><aside class="station-card cta-panel"><h2>Use this in the app</h2><p>Find a station, favorite it, and keep the tide curve ready before you leave the house.</p><a class="app-cta" href="https://apps.apple.com/app/apple-store/id{APP_ID}?pt=119725640&ct=seo-station-ca-index&mt=8">Get RipCat free</a><p class="notice">NOAA data. Tide predictions are not guarantees or navigation advice.</p></aside></section></main>{footer()}</body></html>'''
(station_dir / 'index.html').write_text(index_html, encoding='utf-8')

for s in stations:
    nearby = sorted([x for x in all_ca if x['id'] != s['id']], key=lambda x: distance(s,x))[:5]
    surf, fish, harbor = use_blocks(s['name'])
    blocks=[]
    if surf:
        blocks.append(("Surf context", "Use the tide curve as one input for beach and point-break timing. RipCat keeps the nearby buoy and marine advisory picture in the same place, so dawn patrol starts with less tab-hopping."))
    if fish:
        blocks.append(("Fishing context", "Moving water matters. Favorite this station in RipCat to check the tide window, nearby water temperature, wind, and wave history before the first cast."))
    if harbor:
        blocks.append(("Boating context", "For harbor timing, pair the station tide with NWS marine zones and buoy observations in RipCat. It is a planning tool, not a replacement for charts, local rules, or judgment."))
    if not blocks:
        blocks.append(("Local planning context", "This station is useful as a local tide reference. Use RipCat for the live curve, nearby stations, and official marine weather context where available."))
    block_html = ''.join(f'<section class="station-card"><h2>{escape(title)}</h2><p>{escape(text)}</p></section>' for title,text in blocks)
    nearby_html = ''.join(f"<li><a href=\"/tides/ca/{n['slug']}/\">{escape(n['name'])}</a><br><small>{distance(s,n):.0f} mi · NOAA {n['id']}</small></li>" for n in nearby)
    breadcrumb_ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"RipCat","item":"https://ripcat.dev/"},{"@type":"ListItem","position":2,"name":"California tide stations","item":"https://ripcat.dev/tides/ca/"},{"@type":"ListItem","position":3,"name":f"{s['name']} Tide Chart & Times","item":f"https://ripcat.dev/tides/ca/{s['slug']}/"}]}
    place_ld = {"@context":"https://schema.org","@type":"Place","name":f"{s['name']} NOAA Tide Station","geo":{"@type":"GeoCoordinates","latitude":float(s['lat']),"longitude":float(s['lng'])},"identifier":s['id'],"address":{"@type":"PostalAddress","addressRegion":"CA","addressCountry":"US"},"url":f"https://ripcat.dev/tides/ca/{s['slug']}/"}
    html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{escape(s['name'])} Tide Chart & Times | RipCat</title><meta name="description" content="NOAA tide station {s['id']} for {escape(s['name'])}, California. Get live tide predictions, nearby buoys, and marine advisories in RipCat."><meta name="apple-itunes-app" content="app-id={APP_ID}, app-argument=ripcat://station/{s['id']}"><meta property="og:title" content="{escape(s['name'])} Tide Chart & Times"><meta property="og:description" content="NOAA station {s['id']} in {escape(region_for(float(s['lat'])))}. Get live tides in RipCat."><meta property="og:url" content="https://ripcat.dev/tides/ca/{s['slug']}/"><meta property="og:image" content="https://ripcat.dev/i/og-image.jpg"><link rel="canonical" href="https://ripcat.dev/tides/ca/{s['slug']}/"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="/site.css"><style>{css}</style><script type="application/ld+json">{json.dumps(place_ld,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb_ld,separators=(',',':'))}</script></head><body>{nav()}<main><section class="station-hero"><div class="wrap"><div class="crumbs"><a href="/">RipCat</a> / <a href="/tides/ca/">California tide stations</a> / {escape(s['name'])}</div><div class="station-kicker">NOAA station {s['id']} · {escape(region_for(float(s['lat'])))}</div><h1>{escape(s['name'])} Tide Chart &amp; Times</h1><p class="station-lede">Use this NOAA tide station as the starting point for {escape(s['name'])}. Static pages do not claim today's tide height; open RipCat for the live tide curve, nearby buoys, and official marine advisory context.</p></div></section><section class="wrap station-grid"><div><section class="station-card"><h2>Station facts</h2><div class="fact-grid"><div class="fact"><b>Station ID</b><span>{s['id']}</span></div><div class="fact"><b>Coordinates</b><span>{float(s['lat']):.5f}, {float(s['lng']):.5f}</span></div><div class="fact"><b>Region</b><span>{escape(region_for(float(s['lat'])))}</span></div><div class="fact"><b>Station type</b><span>{escape(station_type(s))}</span></div></div></section><section class="station-card"><h2>How to read this station</h2><p>NOAA tide predictions describe the expected rise and fall of the water at this station. The useful part is often the curve: where the water is in the cycle, whether it is flooding or ebbing, and how much range is left before the next turn.</p><p>Wind, pressure, swell, river flow, and local bathymetry can move real water around. Treat predictions as a planning baseline, then check live observations and local conditions before making a call.</p><p class="notice">RipCat uses official NOAA, National Weather Service, and NDBC data. Predictions and marine forecasts are not navigation advice.</p></section>{block_html}</div><aside><section class="station-card cta-panel"><h2>Get live tides for this station</h2><p>RipCat puts the full tide curve, favorites, nearby buoys, and marine advisories into one Apple-native app.</p><a class="app-cta" href="{app_url(s['id'])}">Open {escape(s['name'])} in RipCat</a><h3>Nearby stations</h3><ul class="nearby-list">{nearby_html}</ul><p style="margin-top:18px"><a href="/tides/ca/">All California pilot stations</a></p></section></aside></section></main>{footer()}</body></html>'''
    out = station_dir / s['slug']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(html, encoding='utf-8')

# Rewrite sitemap with existing core pages plus pilot URLs.
urls = [
    ("https://ripcat.dev/", None),
    ("https://ripcat.dev/pro.html", None),
    ("https://ripcat.dev/privacy-policy.html", None),
    ("https://ripcat.dev/blog/", "2026-07-07"),
    ("https://ripcat.dev/blog/how-tide-predictions-work.html", "2026-07-07"),
    ("https://ripcat.dev/tides/ca/", TODAY),
]
for s in stations:
    urls.append((f"https://ripcat.dev/tides/ca/{s['slug']}/", TODAY))
lines = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc,lastmod in urls:
    if lastmod:
        lines.append(f'  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>')
    else:
        lines.append(f'  <url><loc>{loc}</loc></url>')
lines.append('</urlset>')
(ROOT/'sitemap.xml').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(f"Generated {len(stations)} station pages plus /tides/ca/ from NOAA metadata")
print('\n'.join(f"{s['id']} {s['name']} /tides/ca/{s['slug']}/" for s in stations))
