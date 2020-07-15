# FaceBook-Scraper [2020]
_Scrape posts from any group or user into a .csv file without needing to register for any API access_

____

### How to use it?

* Install python (this is often already installed) and make sure it is at least v3.8.0
    * Windows
        * Install scoop (https://github.com/lukesampson/scoop)
            * Open Powershell and run
                ```
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
                iwr -useb get.scoop.sh | iex                
                ```
        * If that completes successfully, run
            ```
            scoop install python
            ```
* Install virtualenv (https://virtualenv.pypa.io/en/stable/installation.html)
    * Windows: `python -m pip install --user virtualenv`
* Create virtual environment
    * change to repository directory
    * Windows: `python -m venv env`
* Install dependencies `pip install -r requirements.txt`
* Install firefox
* Download geckodriver
* Copy conf.template.py to conf.py and fill in 
    * path to firefox executable
    * path to geckodriver executable
    * facebook credentials

Use `start.py` to collect the data. 
```
usage: start.py [-h] [--pages PAGES [PAGES ...]] [--groups GROUPS [GROUPS ...]][-d DEPTH]
Data Collection
arguments:
  -h, --help            show this help message and exit
  -p, --pages PAGES [PAGES ...]
                        List the pages you want to scrape
                        for recent posts
  
  -g, --groups GROUPS [GROUPS ...]
                        List the groups you want to scrape
                        for recent posts
  
  -d DEPTH, --depth DEPTH
                        How many recent posts you want to gather in
                        multiples of (roughly) 8.
```
Example: ```python start.py --pages feelzesty -d 20```
____
The output is `posts.csv` inside the script folder.

Output is in three columns: PosterName(Author), uTime and Text
