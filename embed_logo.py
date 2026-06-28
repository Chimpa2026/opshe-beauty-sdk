from PIL import Image
import base64, io

img = Image.open('logoopshe.png').convert('RGBA')
img = img.resize((80,80), Image.LANCZOS)
buf = io.BytesIO()
img.save(buf, 'PNG', optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
logo_data = 'data:image/png;base64,' + b64

content = open('ar_demo.html', encoding='utf-8').read()
content = content.replace('src="/logo"', f'src="{logo_data}"')
content = content.replace("src='/logo'", f"src='{logo_data}'")
content = content.replace("logoImg.src = '/logo';", f"logoImg.src = '{logo_data}';")
open('ar_demo.html', 'w', encoding='utf-8').write(content)
print('Done! Logo embedded.')