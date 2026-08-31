import json
from pathlib import Path

path = Path('products.json')
data = json.loads(path.read_text(encoding='utf-8'))

overrides = {
    'VR002': {
        'image': 'products/VR002-thumbnail.png',
        'image_alt': 'ValueRadar VR002 AGARO Elite rechargeable mini electric chopper buying guide',
    },
}

for product in data.get('products', []):
    override = overrides.get(product.get('id'))
    if override:
        product.setdefault('media', {}).update(override)

path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
