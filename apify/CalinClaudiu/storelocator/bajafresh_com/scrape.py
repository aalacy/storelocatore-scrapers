from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def parse_store(store, domain):
    k = {}
    k["url"] = domain

    try:
        k["Name"] = store.find("name").text.strip()
    except Exception:
        k["Name"] = "<MISSING>"

    try:
        k["Latitude"] = store["latitude"]
    except Exception:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = store["longitude"]
    except Exception:
        k["Longitude"] = "<MISSING>"

    try:
        k["Address"] = store.find("address").text.strip()
    except Exception:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = store.find("city").text.strip()
    except Exception:
        k["City"] = "<MISSING>"

    try:
        k["State"] = store.find("state").text.strip()
    except Exception:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = store.find("zip").text.strip()
    except Exception:
        k["Zip"] = "<MISSING>"

    try:
        k["CountryCode"] = store.find("countrycode").text.strip()
    except Exception:
        k["CountryCode"] = "<MISSING>"

    try:
        k["Phone"] = store.find("phone").text.strip()
    except Exception:
        k["Phone"] = "<MISSING>"

    try:
        k["StoreId"] = store["id"]
    except Exception:
        k["StoreId"] = "<MISSING>"

    try:
        k["hours"] = "; ".join(list(store.find("storehours").stripped_strings))
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        k["StatusName"] = store.find("locationtype").text.strip()
    except Exception:
        k["StatusName"] = "<MISSING>"

    try:
        k["StatusName"] = k["StatusName"] + "-" + store.find("statusname").text.strip()
        k["StatusName"] = k["StatusName"].replace("Under Construction", "Coming Soon")
    except Exception:
        k["StatusName"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://locator.kahalamgmt.com/locator/data/"
    url2 = ".xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()

    page = 25
    domain = "https://www.bajafresh.com/"

    son = session.get(url + str(page) + url2, headers=headers)
    soup = b4(son.text, "lxml")
    stores = soup.find("stores")
    stores = stores.find_all("store")

    for i in stores:
        yield (parse_store(i, domain))

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=MappingField(mapping=["url"]),
        page_url=MultiMappingField(
            mapping=[["url"], ["StoreId"]], multi_mapping_concat_with="/stores/"
        ),
        location_name=MappingField(mapping=["Name"], is_required=False),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(mapping=["Address"], value_transform=fix_comma),
        city=MappingField(
            mapping=["City"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        state=MappingField(
            mapping=["State"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["CountryCode"]),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("() -", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["StoreId"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(mapping=["StatusName"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pinkberry.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
