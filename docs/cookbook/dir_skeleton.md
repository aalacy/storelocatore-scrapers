# Cookbook - Directory & File Skeleton
## Standard Crawl Skeleton:
> Copied over from `./templates/python/object_oriented/< type >` OR: `./templates/python/succinct/< type >`
```bash
/
  Dockerfile        
  scrape.py
  requirements.txt  # <- see section on generating this
  .gitignore
  cp_scripts.sh     # <- run this script to copy scripts to current dir.
  run_scraper.sh    # <- [copied]
  validate.py       # <- [copied]
  apify_to_csv.py   # <- [copied]
  csv-differ.py     # <- [copied]
```

### When starting a work on a new crawler...
1. Create the directory in the Jira ticket headline.
2. Copy files over from the template to the crawler dir.
3. Run `./cp_scripts.sh` to copy useful scripts to the current dir.

### Absolutely make sure that:
1. You generate a `requirements.txt` file. See our [official guide](./reqfile.md).
1. Your crawler works in Docker.
2. To do that, you can run `./run_scraper.sh`
    * If you're running it in Windows, make sure to `./run_scraper.sh --windows`
3. Make sure that `python3 validate.py` runs successfully, and write down all the exceptions in the `README.md` of your 
   crawler dir.
