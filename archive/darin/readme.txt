Store Location Scrapers Readme.txt

Each store location scraper is written in Python 2.7.
Some scraping scripts will require the Python 'requests' package - can be installed by 'pip install requests'

Running each scraper will pull the location data into a csv file named similar to the scraping script,
i.e. marriott.py will create Marriott.csv - PLEASE NOTE, any previous Marriott.csv file in the destination
directory will be OVERWRITTEN, so either rename or move the previously created csv file if you want to keep
it as a backup.

Each .py script has a line near the top like this:

path = '.'  ### this is a relative path for where the output file will be put

Put the relative path (from the directory the script is in) to where you want the destination csv file to be
created...i.e. '../csvfiles/' or '/csvdirectory/marriott' - the default is '.' which is the current directory
where the script is run from.