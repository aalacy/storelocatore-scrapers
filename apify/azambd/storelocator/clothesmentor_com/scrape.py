import json

from sgscrape.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sglogging import sglog
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "clothesmentor.com"
MISSING = "<MISSING>"

website = "https://clothesmentor.com"

log = sglog.SgLogSetup().get_logger(logger_name=website)
api_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8219/stores.js?callback=SMcallback2"


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


# As selenium so cleaning HTML tags to get solid JSON
def getJsonObj(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace(")</pre></body></html>", "")
    )
    return html_string


def fetch_data():
    driver = get_driver(api_url)
    response = driver.page_source

    jsonobj = getJsonObj(response.split("SMcallback2(")[1])

    jsonData = json.loads(jsonobj)
    for d in jsonData["stores"]:
        store_number = d["id"]
        log.info(f"Fetching data from API and now at Store# {store_number}")
        phone = d["phone"]
        page_url = d["url"]
        latitude = d["latitude"]
        longitude = d["longitude"]
        street_address = d["address"].replace("&amp;", "&")
        hours = d["custom_field_1"]
        hours_of_operation = hours.replace("&amp;", ",")
        location_name = d["name"]
        addrs = parse_address_intl(
            location_name.split("#")[0].replace("Store", "").strip()
        )
        if "," in location_name:
            city = location_name.split(", ")[0]
            state = location_name.split(", ")[-1].split()[0]
        else:
            city = addrs.city
            state = addrs.state

        location_type = "Store"
        country_code = "US"
        zip_postal = MISSING

        yield {
            "locator_domain": DOMAIN,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": street_address,
            "state": state,
            "zip": zip_postal,
            "phone": phone,
            "location_type": location_type,
            "hours": hours_of_operation,
            "country_code": country_code,
        }

    driver.quit()


# is require false means if missing then it will add row
def scrape():
    log.info(f"Start Crawling {website} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
