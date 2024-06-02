import os
import re
from send2trash import send2trash


def get_image_references_from_md(md_folder):
    image_references = set()

    # Regex for Markdown image syntax: ![alt text](image_url)
    md_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    # Regex for HTML image tag: <img src="image_url" ...>
    html_pattern = re.compile(r'<img\s+.*?src=["\'](.*?)["\']')

    for root, dirs, files in os.walk(md_folder):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Find all matches for both Markdown and HTML patterns
                    md_matches = md_pattern.findall(content)
                    html_matches = html_pattern.findall(content)

                    # Add the basename of each match to the set
                    for match in md_matches + html_matches:
                        image_references.add(os.path.basename(match))

    return image_references


def get_images_from_assets(assets_folder):
    image_files = set()
    for root, dirs, files in os.walk(assets_folder):
        for file in files:
            image_files.add(file)
    return image_files


def delete_unreferenced_images(assets_folder, unreferenced_images):
    removed_count = 0
    for image in unreferenced_images:
        image_path = os.path.join(assets_folder, image)
        if os.path.exists(image_path):
            # Move file to trash instead of deleting permanently
            send2trash(image_path)
            print(f"Moved to trash: {image_path}")
            removed_count += 1
    return removed_count


def process_folder(folder):
    total_removed = 0
    for root, dirs, files in os.walk(folder, topdown=True):
        if '.git' in dirs:
            dirs.remove('.git')  # 在 topdown 模式下移除 .git 文件夹
        for dir in dirs:
            if 'assets' in dir:
                assets_folder = os.path.join(root, dir)
                if os.path.isdir(assets_folder):
                    md_folder = root
                    image_references = get_image_references_from_md(md_folder)
                    all_images = get_images_from_assets(assets_folder)

                    unreferenced_images = all_images - image_references
                    if unreferenced_images:
                        print(
                            f"Unreferenced images in {assets_folder} to be moved to trash: {unreferenced_images}")
                        removed_count = delete_unreferenced_images(
                            assets_folder, unreferenced_images)
                        total_removed += removed_count
                    else:
                        print(
                            f"No unreferenced images found in {assets_folder}")
    print(f"Total removed images: {total_removed}")


if __name__ == "__main__":
    note_folder = r"D:\work\note\core\note"
    process_folder(note_folder)
