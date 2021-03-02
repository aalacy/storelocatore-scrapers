# Cookbook - Directory & File Skeleton
## Standard Crawl Skeleton:
> Copied over from `./templates/python/object_oriented/< type >` OR: `./templates/python/succinct/< type >`
```bash
/
  Dockerfile        
  scrape.py
  requirements.txt  # <- see section on generating this
  .gitignore
  run_scraper.sh    # <- copy over from ./scripts/
  validate.py       # <- copy over from ./scripts/
```

### When starting a work on a new crawler...
1. Create the directory in the Jira ticket headline.
2. Copy files over from the template to the crawler dir.
3. Copy `./scripts/run_scraper.sh` and `./scripts/validate.py` to the crawler dir.

### Absolutely make sure that:
1. Your crawler works in Docker.
2. To do that, you can run `./run_scraper.sh`
    * If you're running it in Windows, make sure to `./run_scraper.sh --windows`
3. Make sure that `python3 validate.py` runs successfully, and write down all the exceptions in the `README.md` of your 
   crawler dir.

### Generating the requirements.txt file
Your `requirements.txt` file should include _all_ the dependencies the crawler will require, together with their exact 
versions.

An easy way to do that, is:
1. Navigate to the new crawl folder.
2. Execute `python3 -m venv .` to create a local virtual environment.
3. Run `pip install sgcrawler` to get the latest supported versions of most libraries.
4. Run `pip freeze`, and paste the output to `requirements.txt`. In bash: `pip freeze > requirements.txt`
