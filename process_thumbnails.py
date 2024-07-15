import os
import cloudinary
import cloudinary.uploader
from github import Github
from PIL import Image
import requests
from io import BytesIO
import logging

logging.basicConfig(level=logging.INFO)

# Konfigurace Cloudinary
cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET']
)

# Konfigurace GitHub
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo(f"{os.environ['GITHUB_REPO_OWNER']}/{os.environ['GITHUB_REPO_NAME']}")

def process_thumbnail(url):
    logging.info(f"Processing thumbnail: {url}")
    # Stáhnout obrázek
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    # Nahrát do Cloudinary a získat URL
    result = cloudinary.uploader.upload(url, width=300, height=200, crop="fill")
    logging.info(f"Uploaded to Cloudinary: {result['secure_url']}")
    return result['secure_url']

def update_post_content(content, new_thumbnail_url):
    # Aktualizovat obsah postu s novým URL thumbnailu
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('thumbnail:'):
            lines[i] = f'thumbnail: {new_thumbnail_url}'
            logging.info(f"Updated thumbnail URL to: {new_thumbnail_url}")
            break
    return '\n'.join(lines)

def main():
    logging.info("Starting thumbnail processing")
    # Procházet všechny soubory v _posts adresáři
    contents = repo.get_contents("_posts")
    processed_count = 0
    for content_file in contents:
        if content_file.name.endswith('.md'):
            logging.info(f"Processing file: {content_file.name}")
            file_content = content_file.decoded_content.decode('utf-8')
            
            # Najít URL thumbnailu
            thumbnail_url = None
            for line in file_content.split('\n'):
                if line.startswith('thumbnail:'):
                    thumbnail_url = line.split(':', 1)[1].strip()
                    break
            
            if thumbnail_url:
                # Zpracovat thumbnail
                new_thumbnail_url = process_thumbnail(thumbnail_url)
                
                # Aktualizovat obsah souboru
                updated_content = update_post_content(file_content, new_thumbnail_url)
                
                # Commitnout změny zpět do repozitáře
                repo.update_file(
                    content_file.path,
                    f"Update thumbnail for {content_file.name}",
                    updated_content,
                    content_file.sha
                )
                logging.info(f"Updated thumbnail for {content_file.name}")
                processed_count += 1
            else:
                logging.info(f"No thumbnail found for {content_file.name}")
    
    logging.info(f"Finished thumbnail processing. Processed {processed_count} thumbnails.")

if __name__ == "__main__":
    main()