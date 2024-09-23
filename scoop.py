import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re
import signal
import sys
from tqdm import tqdm

# Signal handler to handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print("\nDownload interrupted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_mp3s_from_url(url, output_folder="mp3_files"):
    visited_pages = set()  # Keep track of visited pages to avoid duplicates

    def download_file_with_progress(mp3_url, file_path):
        temp_file_path = file_path + ".part"  # Temporary filename
        try:
            response = requests.get(mp3_url, stream=True, timeout=10)
            response.raise_for_status()

            total_size = int(response.headers.get('Content-Length', 0))
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(file_path))

            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=10240):  # Larger chunk size
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

            progress_bar.close()

            if total_size != 0 and progress_bar.n != total_size:
                print(f"Warning: Download incomplete for {file_path}")
            
            # Rename the temp file to the final filename after successful download
            os.rename(temp_file_path, file_path)

        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Failed to download: {mp3_url}. Error: {e}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)  # Delete the partial file on error

        finally:
            # Clean up the progress bar if interrupted
            progress_bar.close()

    def download_from_page(page_url):
        if page_url in visited_pages:
            return  # Avoid revisiting the same page

        print(f"Fetching page: {page_url}")
        visited_pages.add(page_url)

        response = requests.get(page_url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve the page: {page_url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        page_title = soup.title.string.strip() if soup.title else "Untitled"
        sanitized_title = sanitize_filename(page_title)
        page_folder = os.path.join(output_folder, sanitized_title)

        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        mp3_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.mp3')]

        if not mp3_links:
            print(f"No MP3 files found on this page: {page_url}")
        else:
            for mp3_link in mp3_links:
                mp3_url = urljoin(page_url, mp3_link)
                file_name = os.path.join(page_folder, os.path.basename(mp3_link))

                if os.path.exists(file_name):
                    print(f"File already exists, skipping: {file_name}")
                    continue

                print(f"Downloading {mp3_url}...")
                download_file_with_progress(mp3_url, file_name)

        pagination_links = soup.find("div", class_="page-links")
        if pagination_links:
            for a_tag in pagination_links.find_all('a', class_="post-page-numbers"):
                next_page_url = a_tag.get('href')
                if next_page_url:
                    download_from_page(next_page_url)

    download_from_page(url)


# Example usage
url = "https://example.com/page-with-mp3s"
download_mp3s_from_url(url)
