from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

MISSING = "<MISSING>"
DOMAIN = "countryroad.com.au"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

stores_page = "https://www.countryroad.com.au/sitemap#stores"


class_name1 = "stores"
class_name2 = "detail"


def fetch_page_from_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
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

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver.page_source


def parse_data(soup, page_url):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = soup.select_one("h1").text
    data["store_number"] = MISSING

    data["page_url"] = page_url
    data["location_type"] = ""
    street_address = soup.select_one('span[itemprop="streetAddress"]').text
    street_address2 = soup.select_one('span[itemprop="streetAddress2"]').text
    if street_address2 is not MISSING:
        street_address = street_address + street_address2
    data["street_address"] = street_address
    data["city"] = soup.select_one('span[itemprop="addressLocality"]').text
    data["state"] = soup.select_one('span[itemprop="addressRegion"]').text

    if "/nz/" in page_url:
        country_code = "NZ"
    elif "/gt/" in page_url:
        country_code = "ZA"
    elif "/fs/" in page_url:
        country_code = "ZA"
    else:
        country_code = "AU"

    data["country_code"] = country_code
    data["zip_postal"] = soup.select_one('span[itemprop="postalCode"]').text
    phone = soup.select_one('span[itemprop="telephone"]').text
    data["phone"] = phone
    logger.info(f"Phone Number: {phone}")
    data["latitude"] = soup.select_one('div.coordinates meta[itemprop="latitude"]').get(
        "content"
    )
    data["longitude"] = soup.select_one(
        'div.coordinates meta[itemprop="longitude"]'
    ).get("content")
    hours = soup.select("div.opening-hours div.content tr")
    hoo = []
    for h in hours:
        day = h.select("td")[0].text
        hrs = h.select("td")[1].text
        hoo.append(f"{day}:{hrs}")
    data["hours_of_operation"] = ", ".join(hoo)

    return data


def fetch_data():

    htmlsource = fetch_page_from_driver(stores_page, class_name1, driver=None)

    soup = bs(htmlsource, "html.parser")

    stores = soup.select("section.stores div.sitemap_catalogue li")
    logger.info(f"Total Stores: {len(stores)}")
    for store in stores:
        page_url = f"https://www.countryroad.com.au{store.select_one('a')['href']}"
        logger.info(f"Crawling: {page_url}")
        htmldetail = fetch_page_from_driver(page_url, class_name2)
        soup_detail_page = bs(htmldetail, "html.parser")
        i = parse_data(soup_detail_page, page_url)
        yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ..")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
