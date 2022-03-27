from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome

from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

MISSING = "<MISSING>"
DOMAIN = "countryroad.com.au"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

stores_page = "https://www.countryroad.com.au/sitemap#stores"


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
    data["country_code"] = "NZ" if "/nz/" in page_url else "AU"
    data["zip_postal"] = soup.select_one('span[itemprop="postalCode"]').text
    data["phone"] = soup.select_one('span[itemprop="telephone"]').text
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
    with SgChrome() as driver:

        driver.get(stores_page)

        soup = bs(driver.page_source, "html.parser")

        stores = soup.select("section.stores div.sitemap_catalogue li")
        logger.info(f"Total Stores: {len(stores)}")
        for store in stores:
            page_url = f"https://www.countryroad.com.au{store.select_one('a')['href']}"
            logger.info(f"Crawling: {page_url}")
            driver.get(page_url)
            soup_detail_page = bs(driver.page_source, "html.parser")
            i = parse_data(soup_detail_page, page_url)
            yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
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