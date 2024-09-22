import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin


def download_mp3s_from_url(url, output_folder="mp3_files"):
    # Step 1: Fetch the webpage
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page: {url}")
        return

    # Step 2: Parse the webpage content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 3: Find all links to mp3 files
    mp3_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.mp3')]
    
    if not mp3_links:
        print("No MP3 files found on the page.")
        return
    
    # Step 4: Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Step 5: Download each MP3 file
    for mp3_link in mp3_links:
        mp3_url = urljoin(url, mp3_link)  # Handle relative links
        file_name = os.path.join(output_folder, os.path.basename(mp3_link))
        
        print(f"Downloading {mp3_url}...")
        mp3_response = requests.get(mp3_url)
        
        if mp3_response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(mp3_response.content)
            print(f"Saved: {file_name}")
        else:
            print(f"Failed to download: {mp3_url}")


# Example usage
url = "https://dailyaudiobooks.co/the-immortal-life-henrietta-lacks-audiobook-2/"
download_mp3s_from_url(url)
