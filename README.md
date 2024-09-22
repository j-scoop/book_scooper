### How to use
Set up your virtual environment by running `python -m venv venv` from the project directory

activate your virtual environment and install dependencies by running `pip install -r requirements.txt`

Add your url to the 'url' variable in downloader.py `url = "https://www.site.com/your-audiobook-page"`

Execute `python downloader.py` from the project directory. The script will then download all .mp3 files on the webpage and store them in the /mp3_files/ directory
