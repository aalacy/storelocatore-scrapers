# Basic Setup
> [First, read this Quick-Start section](https://docs.google.com/document/d/1LZEzE2lmhOAtAb8jgnVUjKyTzxblEBTvO-XaF6C5k6g/edit#heading=h.vrpdfang5k6v)
## Installation Requirements
_Please see online installation guides for your operating system._ 

_For the smoothest experience, consider using a *nix system for development,
like Linux or Mac OS_

### Absolutely Required
* `docker` - this will enable you to run your scraper *__the same way as in production__*. 
  This is extremely important, since you can eliminate issues stemming from library version differences,
  and save time discovering and addressing issues.

### Required to run locally
* `python3` - this will allow you to execute your code locally, for a quicker turnaround. Minimum version: `3.8.0`.
* `libpostal` - this library will allow you to use address parsing in your crawls.
* `chromedriver`, `geckodriver` - these will allow you to use a headless browser.
* `venv` - It's recommended (but not required) that you use a `venv` to manage your Python libraries. 
    * See our [official virtual environment guide](./cookbook/reqfile.md) for installation and usage.
    

## To run your scraper:
### In Docker
1. Copy `run_scraper.sh` from the `scripts` dir to your scraper directory.
2. Execute `run_scraper.sh` from command-line/shell. 
   * **_It is a Bash script, so make sure you execute using Bash._**
    ```bash
    ./run_scraper.sh
    ```

> #### Tips & Tricks:
* Use `docker system prune -a` to periodically de-clutter your computer from docker images and drives.
* Run `run_scraper.sh --debug` to start your docker in interactive-shell mode. This will not automatically run the scraper - you can do it from within the running Docker instance to debug anything.

### Locally
Your scraper should always be runnable as:
```bash
python3 scrape.py
```

This will generate a `data.csv` file in your local dir. Each run will overwrite this file (unless you've specifically taken steps not to).

## Validating your results:
> [First, consult this section on validation](https://docs.google.com/document/d/1LZEzE2lmhOAtAb8jgnVUjKyTzxblEBTvO-XaF6C5k6g/edit#heading=h.vrpdfang5k6v)

1. Copy `validate.py` to the local crawl dir.
2. Run it on the resulting `./apify_docker_storage` records, like so:
```bash
python3 validate.py ./apify_docker_storage
```

_You should **always** validate the results of your `Docker` run before committing!_

## Formatting Code
> TODO

## Using proxies
* Many websites and APIs will require the IP to be local to the country.
* To that end, we're using `Apify`'s proxies.
* `Apify` provides both residential and centralized proxies.
* To use a proxy, always set it as an env variable. See the next section on bash utils for details 
  (and it might be different in Windows.)


### Some Useful Bash Utils
Helpful utils to put on the PATH, or to keep in mind:

```bash
export SG_HOME="<...>"
export SG_PROXY_PASSWORD="<...>"

function sg_proxy_prod() {
        export PROXY_URL="http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
        export PROXY_PASSWORD="$SG_PROXY_PASSWORD"
}

function sg_proxy_residential_by_country(){
        export PROXY_URL="http://groups-RESIDENTIAL,country-"$1":{}@proxy.apify.com:8000/"
        export PROXY_PASSWORD="$SG_PROXY_PASSWORD"
}
function sg_no_proxy(){
        unset PROXY_URL
        unset PROXY_PASSWORD
}

function sg_cp_run_script(){
        cp "${SG_HOME}"/crawl-service/scripts/run_scraper.sh . && \
        chmod +x run_scraper.sh
}
```