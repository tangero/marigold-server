import os
import re
import requests
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
import cloudinary

# Nastavení Cloudinary
cloudinary.config(
    cloud_name = "your_cloud_name",
    api_key = "your_api_key",
    api_secret = "your_api_secret"
)

def process_thumbnail(url):
    # Upravit obrázek pomocí Cloudinary
    result = upload(url, width=300, height=200, crop="fill")
    # Stáhnout upravený obrázek
    response = requests.get(result['url'])
    filename = os.path.basename(url)
    new_path = f"/assets/{filename}"
    with open(f".{new_path}", "wb") as f:
        f.write(response.content)
    return new_path

def update_post(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Najít URL thumbnail v front matter
    match = re.search(r'thumbnail:\s*(.*)', content)
    if match:
        old_url = match.group(1).strip()
        new_url = process_thumbnail(old_url)
        # Aktualizovat URL v obsahu
        content = content.replace(old_url, new_url)

        with open(file_path, 'w') as file:
            file.write(content)

def main():
    posts_dir = './_posts'  # Upravte podle vaší struktury
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            update_post(os.path.join(posts_dir, filename))

if __name__ == "__main__":
    main()
