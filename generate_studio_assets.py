import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_studio_canvas():
    # 800x800 high-res canvas with pure white studio background
    img = Image.new("RGBA", (800, 800), (255, 255, 255, 255))
    return img

def add_soft_shadow(base, bbox):
    # Add subtle studio floor reflection / soft shadow underneath product
    shadow = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = bbox
    s_draw.ellipse([x1, y2 - 20, x2, y2 + 30], fill=(200, 205, 215, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, shadow)

target_dir = os.path.join(os.path.dirname(__file__), "static", "assets")

# 1. Dettol Liquid Handwash
img1 = create_studio_canvas()
img1 = add_soft_shadow(img1, (260, 160, 540, 680))
draw = ImageDraw.Draw(img1)
# Bottle Body
draw.rounded_rectangle([280, 260, 520, 640], radius=40, fill="#10b981", outline="#059669", width=4)
# Clear window/label
draw.rounded_rectangle([310, 340, 490, 580], radius=20, fill="#ffffff", outline="#e2e8f0", width=2)
draw.text((345, 380), "DETTOL", fill="#059669", font_size=32)
draw.text((330, 430), "HANDWASH", fill="#0f172a", font_size=24)
draw.text((345, 480), "100% Germ", fill="#64748b", font_size=18)
draw.text((350, 510), "Protection", fill="#64748b", font_size=18)
# Pump Neck & Head
draw.rectangle([370, 190, 430, 260], fill="#f8fafc", outline="#cbd5e1", width=3)
draw.rounded_rectangle([330, 160, 470, 195], radius=10, fill="#f1f5f9", outline="#cbd5e1", width=3)
img1.convert("RGB").save(os.path.join(target_dir, "dettol.png"))

# 2. Samsung LED TV
img2 = create_studio_canvas()
img2 = add_soft_shadow(img2, (120, 220, 680, 580))
draw = ImageDraw.Draw(img2)
# TV Frame
draw.rectangle([140, 200, 660, 520], fill="#0f172a", outline="#334155", width=6)
# Inner Display Screen with rich color wallpaper
draw.rectangle([152, 212, 648, 508], fill="#1e1b4b")
# Screen graphics
draw.ellipse([200, 250, 450, 480], fill="#4f46e5")
draw.ellipse([350, 230, 600, 490], fill="#7c3aed")
draw.text((330, 340), "SAMSUNG", fill="#ffffff", font_size=28)
# TV Stand Legs
draw.line([(220, 520), (180, 590)], fill="#334155", width=10)
draw.line([(580, 520), (620, 590)], fill="#334155", width=10)
img2.convert("RGB").save(os.path.join(target_dir, "samsung-led-tv.png"))

# 3. Parle-G Biscuits
img3 = create_studio_canvas()
img3 = add_soft_shadow(img3, (200, 220, 600, 620))
draw = ImageDraw.Draw(img3)
# Biscuit Wrapper
draw.rounded_rectangle([220, 240, 580, 600], radius=25, fill="#facc15", outline="#eab308", width=4)
# Red Brand Strip
draw.rectangle([220, 340, 580, 480], fill="#dc2626")
draw.text((310, 360), "Parle-G", fill="#ffffff", font_size=52)
draw.text((285, 430), "ORIGINAL GLUCOSE", fill="#fef08a", font_size=20)
draw.text((320, 520), "Wheat & Milk", fill="#854d0e", font_size=22)
img3.convert("RGB").save(os.path.join(target_dir, "parle-g.png"))

# 4. Lakme Lipstick
img4 = create_studio_canvas()
img4 = add_soft_shadow(img4, (300, 160, 500, 680))
draw = ImageDraw.Draw(img4)
# Black Base Case
draw.rounded_rectangle([320, 400, 480, 660], radius=15, fill="#0f172a", outline="#334155", width=3)
# Gold Collar
draw.rectangle([340, 320, 460, 400], fill="#eab308", outline="#ca8a04", width=2)
# Lipstick Bullet (Red Slanted Tip)
draw.polygon([(350, 320), (450, 320), (450, 200), (350, 160)], fill="#b91c1c")
draw.text((360, 480), "LAKMÉ", fill="#eab308", font_size=24)
draw.text((365, 530), "MATTE", fill="#ffffff", font_size=18)
img4.convert("RGB").save(os.path.join(target_dir, "lakme-lipstick.png"))

# 5. Tide Detergent
img5 = create_studio_canvas()
img5 = add_soft_shadow(img5, (220, 180, 580, 660))
draw = ImageDraw.Draw(img5)
# Orange Detergent Pouch
draw.rounded_rectangle([240, 200, 560, 640], radius=35, fill="#f97316", outline="#ea580c", width=4)
# Bullseye Target Logo
draw.ellipse([290, 280, 510, 500], fill="#facc15")
draw.ellipse([320, 310, 480, 470], fill="#dc2626")
draw.ellipse([350, 340, 450, 440], fill="#ffffff")
draw.text((360, 370), "Tide", fill="#1e3a8a", font_size=42)
draw.text((310, 540), "LEMON & MINT", fill="#ffffff", font_size=24)
img5.convert("RGB").save(os.path.join(target_dir, "tide-detergent.png"))

# 6. Bournvita
img6 = create_studio_canvas()
img6 = add_soft_shadow(img6, (240, 180, 560, 660))
draw = ImageDraw.Draw(img6)
# Jar Tub
draw.rounded_rectangle([260, 220, 540, 640], radius=30, fill="#78350f", outline="#451a03", width=4)
# Orange Cap
draw.rounded_rectangle([250, 160, 550, 230], radius=15, fill="#f97316", outline="#ea580c", width=3)
# Label
draw.rounded_rectangle([280, 300, 520, 560], radius=15, fill="#ffffff", outline="#e2e8f0", width=2)
draw.text((300, 330), "Cadbury", fill="#7c3aed", font_size=22)
draw.text((290, 370), "Bournvita", fill="#78350f", font_size=38)
draw.text((315, 450), "HEALTH DRINK", fill="#f97316", font_size=18)
draw.text((320, 490), "Vitamin D + C", fill="#16a34a", font_size=18)
img6.convert("RGB").save(os.path.join(target_dir, "bournvita.png"))

# 7. Amul Butter
img7 = create_studio_canvas()
img7 = add_soft_shadow(img7, (180, 240, 620, 600))
draw = ImageDraw.Draw(img7)
# Butter Brick Box
draw.rounded_rectangle([200, 260, 600, 580], radius=20, fill="#fef08a", outline="#eab308", width=4)
# Red Banner
draw.rectangle([200, 340, 600, 460], fill="#dc2626")
draw.text((330, 365), "Amul", fill="#ffffff", font_size=52)
draw.text((300, 480), "BUTTER", fill="#854d0e", font_size=40)
draw.text((280, 535), "Utterly Butterly Delicious", fill="#dc2626", font_size=18)
img7.convert("RGB").save(os.path.join(target_dir, "amul-butter.png"))

# 8. Colgate Toothpaste
img8 = create_studio_canvas()
img8 = add_soft_shadow(img8, (160, 280, 640, 560))
draw = ImageDraw.Draw(img8)
# Toothpaste Tube (horizontal angled tube)
draw.rounded_rectangle([180, 300, 620, 500], radius=25, fill="#dc2626", outline="#b91c1c", width=4)
# Cap
draw.rounded_rectangle([140, 340, 190, 460], radius=10, fill="#ffffff", outline="#cbd5e1", width=3)
# White Brand Swirl
draw.text((260, 360), "Colgate", fill="#ffffff", font_size=56)
draw.text((270, 430), "STRONG TEETH", fill="#fef08a", font_size=20)
img8.convert("RGB").save(os.path.join(target_dir, "colgate-toothpaste.png"))

print("🎨 Generated 8 high-definition studio product render photography images on clean white backgrounds!")
