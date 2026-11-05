"""RTS Abyss runtime theme and the shared, flat folded-R vector mark."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKENS = json.loads((ROOT / 'design' / 'rts-tokens.json').read_text(encoding='utf-8'))
CORE, SEMANTIC = TOKENS['core'], TOKENS['semantic']
COLORS = {
    'ink': CORE['background'], 'panel': CORE['surface'], 'field': CORE['background'],
    'text': CORE['text'], 'muted': CORE['text_secondary'], 'brand': CORE['brand'],
    'accent': SEMANTIC['primary'], 'accent_hover': SEMANTIC['primary_hover'],
    'accent_pressed': SEMANTIC['primary_pressed'], 'selected': SEMANTIC['selection_background'],
    'selected_text': SEMANTIC['selection_foreground'], 'border': CORE['border_control'],
    'separator': CORE['border_subtle'], 'button': CORE['surface_raised'],
    'button_hover': CORE['surface_hover'], 'disabled': SEMANTIC['disabled_background'],
    'disabled_text': SEMANTIC['disabled_foreground'], 'amber': SEMANTIC['warning'],
    'error': SEMANTIC['error'], 'success': SEMANTIC['success'], 'info': SEMANTIC['info'],
}
# One 100-unit vector definition feeds SVG, Tk and antialiased Windows icons.
# The gaps create the folds; no gradients, shading, or material effects.
MARK_PATHS = (
    (('M', 8, 14), ('L', 69, 14), ('C', 88, 14, 94, 25, 90, 37),
     ('C', 87, 46, 79, 51, 69, 57), ('L', 56, 49), ('L', 71, 40),
     ('C', 78, 36, 78, 29, 69, 29), ('L', 23, 29)),
    (('M', 10, 44), ('L', 39, 29), ('L', 57, 39), ('L', 10, 64)),
    (('M', 10, 69), ('L', 27, 60), ('L', 27, 86), ('L', 10, 86)),
    (('M', 31, 58), ('L', 44, 51), ('L', 94, 86), ('L', 65, 86)),
)


def mark_polygons():
    for commands in MARK_PATHS:
        points = []
        for command in commands:
            if command[0] in ('M', 'L'):
                points.append((command[1], command[2]))
            else:
                x0, y0 = points[-1]
                x1, y1, x2, y2, x3, y3 = command[1:]
                for step in range(1, 25):
                    t = step / 24
                    u = 1 - t
                    points.append((u**3*x0+3*u*u*t*x1+3*u*t*t*x2+t**3*x3,
                                   u**3*y0+3*u*u*t*y1+3*u*t*t*y2+t**3*y3))
        yield points


def draw_mark(canvas, size=52):
    for points in mark_polygons():
        canvas.create_polygon(*[v*size/100 for point in points for v in point],
                              fill=COLORS['brand'], outline='')


def create_assets(directory):
    from PIL import Image, ImageDraw
    directory.mkdir(exist_ok=True)
    image = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for points in mark_polygons():
        draw.polygon([(x*10.24, y*10.24) for x, y in points], fill=COLORS['brand'])
    image.save(directory / 'rts-mark-master.png')
    image.resize((64, 64), Image.Resampling.LANCZOS).save(directory / 'rts-mark.png')
    # Audio Reel product icon: solid silver reel, three open slots, cyan signal.
    import math
    tile = Image.new('RGBA', image.size, (0, 0, 0, 0))
    icon_draw = ImageDraw.Draw(tile)
    unit = 10.24
    icon_draw.rounded_rectangle((0, 0, 1023, 1023), radius=190, fill=COLORS['ink'])
    icon_draw.ellipse((14*unit, 14*unit, 86*unit, 86*unit), fill=COLORS['text'])
    icon_draw.ellipse((33*unit, 33*unit, 67*unit, 67*unit), fill=COLORS['ink'])
    slots = []
    for start, end in ((205, 255), (285, 335), (65, 115)):
        angles = [math.radians(start+(end-start)*i/32) for i in range(33)]
        points = [(50+29*math.cos(t), 50+29*math.sin(t)) for t in angles]
        points += [(50+22*math.cos(t), 50+22*math.sin(t)) for t in reversed(angles)]
        slots.append(points)
        icon_draw.polygon([(x*unit, y*unit) for x,y in points], fill=COLORS['ink'])
    wave = ((38,50),(40,50),(43,45),(47,56),(51,42),(55,55),(59,50),(62,50))
    icon_draw.line([(x*unit,y*unit) for x,y in wave], fill=COLORS['accent'], width=29, joint='curve')
    for x,y in wave:
        icon_draw.ellipse(((x-1.4)*unit,(y-1.4)*unit,(x+1.4)*unit,(y+1.4)*unit),fill=COLORS['accent'])
    tile.save(directory / 'link2audio-icon.png')
    tile.resize((256, 256), Image.Resampling.LANCZOS).save(directory / 'link2audio-icon-preview.png')
    tile.resize((64, 64), Image.Resampling.LANCZOS).save(directory / 'app-icon.png')
    sizes = (16, 24, 32, 48, 64, 128, 256)
    # Render every icon size from the full-resolution master.
    tile.save(directory / 'app.ico', sizes=[(n,n) for n in sizes])
    paths = ''.join('<path d="'+' '.join(c[0]+' '.join(map(str, c[1:])) for c in path)+' Z"/>' for path in MARK_PATHS)
    mark = f'<g fill="{COLORS["brand"]}">{paths}</g>'
    (directory / 'rts-mark.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="RevTek Studios folded R">{mark}</svg>\n')
    (directory / 'rts-logo.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100" role="img" aria-label="RevTek Studios">'
        + mark + f'<g fill="{COLORS["text"]}" font-family="Segoe UI, sans-serif">'
        + '<text x="118" y="48" font-size="32" font-weight="700" letter-spacing="2">REVTEK</text>'
        + '<text x="120" y="73" font-size="14" letter-spacing="7">STUDIOS</text></g></svg>\n')
    slot_svg = ''.join('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in points)+'"/>' for points in slots)
    wave_svg = ' '.join(f'{x},{y}' for x,y in wave)
    (directory / 'link2audio-icon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="RevTek Link2Audio audio reel">'
        + f'<rect width="100" height="100" rx="18.5" fill="{COLORS["ink"]}"/>'
        + f'<circle cx="50" cy="50" r="36" fill="{COLORS["text"]}"/>'
        + f'<g fill="{COLORS["ink"]}"><circle cx="50" cy="50" r="17"/>{slot_svg}</g>'
        + f'<polyline points="{wave_svg}" fill="none" stroke="{COLORS["accent"]}" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/></svg>\n')
