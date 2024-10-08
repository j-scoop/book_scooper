### How to use
Clone the repo `git clone https://github.com/j-scoop/book_scooper.git`

Set up your virtual environment by running `python -m venv venv` from the project directory

Activate your virtual environment `venv\Scripts\activate` on Windows or `source venv/bin/activate` on MacOS/Linux.

With your virtual environment activated, install dependencies by running `pip install -r requirements.txt`

Add your url to the 'url' variable in scoop.py `url = "https://www.site.com/your-audiobook-page"`

Execute `python scoop.py` from the project directory. The script will then download all .mp3 files on the webpage and store them in the /mp3_files/ directory

At the end of the run, check the output to see if any downloads timed out. If so, delete the failed file if the script has not already done so, and rerun the script. The script will skip any files already downloaded.

Likewise, sometimes a run may slow down significantly after downloading a few files. Feel free to cancel the run using `ctrl + C`, delete the partially downloaded 'mp3.part' file, and rerun the script. It will pick up from where it was cancelled and will likely run quickly again.
