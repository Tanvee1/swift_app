import urllib.request
import os

images = {
    "dettol.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Liquid_soap_in_bottle_with_pump.jpg/800px-Liquid_soap_in_bottle_with_pump.jpg",
    "samsung-led-tv.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Smart_TV.jpg/800px-Smart_TV.jpg",
    "parle-g.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Plain-Biscuit.jpg/800px-Plain-Biscuit.jpg",
    "lakme-lipstick.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Red_lipstick_tube.jpg/800px-Red_lipstick_tube.jpg",
    "tide-detergent.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Laundry_detergent_box.jpg/800px-Laundry_detergent_box.jpg",
    "bournvita.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Chocolate_powder_jar.jpg/800px-Chocolate_powder_jar.jpg",
    "amul-butter.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Butter_block.jpg/800px-Butter_block.jpg",
    "colgate-toothpaste.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Toothpaste_tube_and_toothbrush.jpg/800px-Toothpaste_tube_and_toothbrush.jpg"
}

target_dir = os.path.join(os.path.dirname(__file__), "static", "assets")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for filename, url in images.items():
    dest_path = os.path.join(target_dir, filename)
    print(f"Downloading high-res studio photo for {filename}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as out_file:
            out_file.write(resp.read())
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed {filename}: {e}")

print("✅ Finished downloading product photography!")
