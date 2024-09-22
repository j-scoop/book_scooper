import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re
from tqdm import tqdm


def sanitize_filename(filename):
    # Remove or replace invalid characters for folder names
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_mp3s_from_url(url, output_folder="mp3_files"):
    visited_pages = set()  # Keep track of visited pages to avoid duplicates

    def download_file_with_progress(mp3_url, file_path):
        try:
            # Make the request with stream=True to download in chunks
            response = requests.get(mp3_url, stream=True, timeout=10)
            response.raise_for_status()  # Raise an exception for bad responses

            # Get the total file size from the headers
            total_size = int(response.headers.get('Content-Length', 0))

            # Initialize a progress bar
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(file_path))

            # Download the file in chunks and update the progress bar
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)
                        progress_bar.update(len(chunk))

            progress_bar.close()

            if total_size != 0 and progress_bar.n != total_size:
                print(f"Warning: Download incomplete for {file_path}")
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Failed to download: {mp3_url}. Error: {e}")

    def download_from_page(page_url):
        if page_url in visited_pages:
            return  # Avoid revisiting the same page

        print(f"Fetching page: {page_url}")
        visited_pages.add(page_url)

        # Step 1: Fetch the webpage
        response = requests.get(page_url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve the page: {page_url}")
            return

        # Step 2: Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 3: Extract the title for folder creation
        page_title = soup.title.string.strip() if soup.title else "Untitled"
        sanitized_title = sanitize_filename(page_title)
        page_folder = os.path.join(output_folder, sanitized_title)

        # Step 4: Create a folder for the current page
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        # Step 5: Find all links to mp3 files
        mp3_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.mp3')]

        if not mp3_links:
            print(f"No MP3 files found on this page: {page_url}")
        else:
            # Step 6: Download each MP3 file
            for mp3_link in mp3_links:
                mp3_url = urljoin(page_url, mp3_link)  # Handle relative links
                file_name = os.path.join(page_folder, os.path.basename(mp3_link))

                # Check if the file already exists
                if os.path.exists(file_name):
                    print(f"File already exists, skipping: {file_name}")
                    continue  # Skip downloading the existing file

                print(f"Downloading {mp3_url}...")
                download_file_with_progress(mp3_url, file_name)

        # Step 7: Find and follow pagination links
        pagination_links = soup.find("div", class_="page-links")
        if pagination_links:
            for a_tag in pagination_links.find_all('a', class_="post-page-numbers"):
                next_page_url = a_tag.get('href')
                if next_page_url:
                    download_from_page(next_page_url)  # Recursively download from the next page

    # Start downloading from the initial page
    download_from_page(url)


# Example usage
# url = "https://example.com/page-with-mp3s"
url = "https://dailyaudiobooks.co/fahrenheit-451/"
download_mp3s_from_url(url)
