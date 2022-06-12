from sgselenium import SgChrome
import time
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

session = SgRequests()

MISSING = "<MISSING>"
DOMAIN = "bbva.es"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "authority": "www.bbva.es",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "referer": "https://www.bbva.es/general/oficinas/valencia/valencia/valencia-pl.-san-agustin/6502",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def get_headersT(url_location):
    with SgChrome() as driver:
        driver.get(url_location)
        time.sleep(20)
        for r in driver.requests:
            if "tsec" in r.headers:
                headers["cookie"] = r.headers["cookie"]
                headers["tsec"] = r.headers["tsec"]

    return headers


url = "https://www.bbva.es/general/oficinas/valencia/valencia/valencia-pl.-san-agustin/6502"
headers = get_headersT(url)


def get_stores(sitemap_url):
    response = session.get(sitemap_url)
    soup = bs(response.text, "lxml")
    locations = soup.select("loc")
    stores = []
    for location in locations:
        page_url = location.text
        store_id = page_url.split("/")[-1]
        if store_id.isnumeric() is False:
            continue

        stores.append(
            {
                "page_url": page_url,
                "store_id": store_id,
            }
        )

    return stores


def get_api(store_id):
    while len(store_id) != 4 and len(store_id) < 4:
        store_id = "0" + store_id

    url = f"https://www.bbva.es/ASO/branches/V01/ES0182{store_id}"
    logger.info(f"URL: {url}")
    querystring = {"$fields": "indicators,closingDate,address,schedules"}
    response = session.get(url, params=querystring, headers=headers)
    logger.info(f"Response: {response}")
    try:
        if len(response.json()["items"]) == 1:
            location = response.json()["items"][0]
        else:
            location = response.json()["items"][1]
    except Exception as e:
        logger.info(f"Failed: {response.status_code} , ERR: {e}")
        pass

    return location


def parse_json(location, page_url):
    data = {}
    data["locator_domain"] = "bbva.es"
    data["store_number"] = location["id"].strip()
    data["page_url"] = page_url
    data["location_name"] = (
        "Oficinas y Cajeros BBVA en "
        + (location["address"]["city"]).capitalize()
        + " — "
        + (location["address"]["name"]).capitalize()
    )
    data["location_type"] = "Oficinas y Cajeros BBVA"
    data["street_address"] = location["address"]["name"].strip()
    data["city"] = location["address"]["city"]
    data["state"] = location["address"]["geographicGroup"][-2]["name"].strip()
    data["country_code"] = location["address"]["geographicGroup"][0]["code"].strip()
    data["zip_postal"] = location["address"]["zipCode"]
    data["phone"] = location["contactsInformation"][0]["name"]
    data["latitude"] = location["address"]["location"].split(",")[1]
    data["longitude"] = location["address"]["location"].split(",")[0]

    schedule = location["schedules"][0]
    ooh = []
    for sch, day in zip(
        schedule["days"],
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ):
        if sch == "1":
            ooh.append(
                day
                + ": "
                + schedule["fromDate"].split("T")[1][:8]
                + " - "
                + schedule["toDate"].split("T")[1][:8]
            )
        elif sch == "0":
            ooh.append(day + ": Closed")
    ooh = ", ".join(ooh)

    data["hours_of_operation"] = ooh
    data["raw_address"] = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["state"],
            data["country_code"],
            data["zip_postal"],
        ]
    )

    return data


def fetch_data():
    stores = get_stores("https://www.bbva.es/sitemap-oficinas.xml")
    logger.info(f"Total Stores ID: {len(stores)}")
    for store in stores:
        page_url = store["page_url"]
        logger.info(f" Page UEL: {page_url}, and StoreID: {store['store_id']}")
        location = get_api(store["store_id"])
        i = parse_json(location, page_url)
        yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
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
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
