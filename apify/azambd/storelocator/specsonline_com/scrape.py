import re
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

session = SgRequests()
DOMAIN = "specsonline.com"
MISSING = "<MISSING>"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

store_sitemap = "https://specsonline.com/maplist-sitemap.xml"

headers = {
    "content-length": "0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "text/html, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6",
}


def parse_json(location, page_url, soup):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = location["title"]
    data["store_number"] = location["cssClass"]
    data["page_url"] = page_url
    data["location_type"] = "Store"
    if "Coming soon" in str(data["location_name"]):
        data["location_type"] = "Coming soon"

    data["street_address"] = location["address"].split("<br")[0].replace("<p>", "")
    data["city"] = (
        (location["address"].split("\n")[1].split(",")[0])
        .replace("</p>", "")
        .replace("<br />", "")
    )
    try:
        data["state"] = re.findall("[A-Z]{2}", location["address"])[0]
    except:
        data["state"] = "<MISSING>"

    data["country_code"] = "US"
    data["zip_postal"] = re.findall(r"\d{5}", location["address"])[0]
    data["phone"] = soup.select_one("span.fa.fa-phone").next_element.strip()
    data["latitude"] = location["latitude"]
    data["longitude"] = location["longitude"]

    data["hours_of_operation"] = soup.select_one(
        "span.fa.fa-clock-o"
    ).next_element.strip()
    data["raw_address"] = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["state"],
            data["zip_postal"],
            data["country_code"],
        ]
    )
    data["raw_address"] = data["raw_address"].replace(MISSING, "")
    data["raw_address"] = " ".join(data["raw_address"].split())
    data["raw_address"] = data["raw_address"].replace(", ,", ",").replace(",,", ",")
    if data["raw_address"][len(data["raw_address"]) - 1] == ",":
        data["raw_address"] = data["raw_address"][:-1]

    return data


def fetch_data():

    response = session.get(store_sitemap, headers=headers)
    logger.info(f"Sitemap Response: {response} ")
    soup = bs(response.text, "lxml")
    stores = [location.text for location in soup.select("loc")]
    logger.info(f"Total Stores: {len(stores)}")

    for store in stores:
        page_url = store
        response_detail = session.get(page_url, headers=headers)
        logger.info(f"{page_url} Response: {response_detail} ")
        soup2 = bs(response_detail.text, "html.parser")
        mapinfo = json.loads(
            re.findall("maplistFrontScriptParams = ({.*})", str(soup2))[0]
        )
        location = json.loads(mapinfo["location"])
        data = parse_json(location, page_url, soup2)
        yield data


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
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
