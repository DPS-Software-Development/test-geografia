"""Convert openpolis Italian regions GeoJSON to a clean, named SVG."""
import json
import math

with open('italy_regions.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Italy bounds
LAT_MIN, LAT_MAX = 35.4, 47.2
LON_MIN, LON_MAX = 6.6, 18.6
LAT_CENTER = (LAT_MIN + LAT_MAX) / 2
COS_LAT = math.cos(math.radians(LAT_CENTER))

WIDTH = 800
SCALE = WIDTH / ((LON_MAX - LON_MIN) * COS_LAT)
HEIGHT = (LAT_MAX - LAT_MIN) * SCALE


def project(lon, lat):
    x = (lon - LON_MIN) * COS_LAT * SCALE
    y = (LAT_MAX - lat) * SCALE
    return x, y


# Map names to canonical short IDs (handles bilingual names)
NAME_TO_ID = {
    "Piemonte": "piemonte",
    "Valle d'Aosta/Vallée d'Aoste": "valle-d-aosta",
    "Lombardia": "lombardia",
    "Trentino-Alto Adige/Südtirol": "trentino-alto-adige",
    "Veneto": "veneto",
    "Friuli-Venezia Giulia": "friuli-venezia-giulia",
    "Liguria": "liguria",
    "Emilia-Romagna": "emilia-romagna",
    "Toscana": "toscana",
    "Umbria": "umbria",
    "Marche": "marche",
    "Lazio": "lazio",
    "Abruzzo": "abruzzo",
    "Molise": "molise",
    "Campania": "campania",
    "Puglia": "puglia",
    "Basilicata": "basilicata",
    "Calabria": "calabria",
    "Sicilia": "sicilia",
    "Sardegna": "sardegna",
}

DISPLAY_NAMES = {
    "Piemonte": "Piemonte",
    "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta",
    "Lombardia": "Lombardia",
    "Trentino-Alto Adige/Südtirol": "Trentino-Alto Adige",
    "Veneto": "Veneto",
    "Friuli-Venezia Giulia": "Friuli-Venezia Giulia",
    "Liguria": "Liguria",
    "Emilia-Romagna": "Emilia-Romagna",
    "Toscana": "Toscana",
    "Umbria": "Umbria",
    "Marche": "Marche",
    "Lazio": "Lazio",
    "Abruzzo": "Abruzzo",
    "Molise": "Molise",
    "Campania": "Campania",
    "Puglia": "Puglia",
    "Basilicata": "Basilicata",
    "Calabria": "Calabria",
    "Sicilia": "Sicilia",
    "Sardegna": "Sardegna",
}


def simplify(points, tolerance):
    """Keep points spaced at least `tolerance` degrees apart (always keep ends)."""
    if len(points) < 4:
        return points
    result = [points[0]]
    for p in points[1:-1]:
        last = result[-1]
        d = math.hypot(p[0] - last[0], p[1] - last[1])
        if d >= tolerance:
            result.append(p)
    result.append(points[-1])
    return result if len(result) >= 4 else points


paths = []
for feature in data['features']:
    name = feature['properties']['reg_name']
    rid = NAME_TO_ID.get(name)
    display = DISPLAY_NAMES.get(name, name)
    if not rid:
        print(f"Skipping unknown region: {name}")
        continue

    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        polygons = [geom['coordinates']]
    elif geom['type'] == 'MultiPolygon':
        polygons = geom['coordinates']
    else:
        continue

    d_parts = []
    for poly in polygons:
        for ring in poly:
            # Skip very tiny rings (smaller than ~3km diameter)
            lons = [p[0] for p in ring]
            lats = [p[1] for p in ring]
            if (max(lons) - min(lons) < 0.03) and (max(lats) - min(lats) < 0.03):
                continue
            simplified = simplify(ring, 0.025)
            if len(simplified) < 3:
                continue
            for i, (lon, lat) in enumerate(simplified):
                x, y = project(lon, lat)
                cmd = 'M' if i == 0 else 'L'
                d_parts.append(f'{cmd}{x:.1f},{y:.1f}')
            d_parts.append('Z')

    d = ''.join(d_parts)
    paths.append(f'<path id="r-{rid}" class="region" data-region="{rid}" data-name="{display}" d="{d}"><title>{display}</title></path>')


svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}" preserveAspectRatio="xMidYMid meet" class="italy-map">
<g>
{chr(10).join(paths)}
</g>
</svg>'''

with open('italy_clean.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print(f"Wrote {len(paths)} regions")
print(f"SVG size: {len(svg_content)} bytes ({len(svg_content)/1024:.1f} KB)")
print(f"Dimensions: {WIDTH:.0f} x {HEIGHT:.0f}")
