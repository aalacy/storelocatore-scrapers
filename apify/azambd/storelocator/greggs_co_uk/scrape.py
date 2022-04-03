from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

import datetime

session = SgRequests(proxy_country="gb")
DOMAIN = "greggs.co.uk"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

api_url = "https://production-digital.greggs.co.uk/api/v1.0/shops?latitude=51.5072178&longitude=-0.1275862&distanceInMeters=80467200"

# 50000 miles = 80467200 Meters


def hoo(hours):

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    dtall = []
    allhours = []
    # Last Date item has been removed becase it was number 8th which is first day for another week cycle
    for i, hr in enumerate(hours[:-1]):

        open_hr_date = hr["openingTime"].split("T")[0]
        dt = datetime.datetime.strptime(open_hr_date, "%Y-%m-%d")
        dt = dt.strftime("%A")
        dtall.append(dt)
        open_time = hr["openingTime"].split("T")[1].replace("Z", "")
        close_time = hr["closingTime"].split("T")[1].replace("Z", "")
        allhours.append(f"{dt}:{open_time}-{close_time}")

    for day in days:
        if day not in dtall:
            allhours.append(f"{day}:Closed")

    hours_of_operation = "; ".join(allhours)

    return hours_of_operation


def parse_json(store):
    data = {}
    data["locator_domain"] = DOMAIN
    data["store_number"] = store["shopCode"]
    data["page_url"] = "<MISSING>"
    data["location_name"] = store["shopName"]
    data["location_type"] = "<MISSING>"
    data["street_address"] = store["address"]["streetName"]
    data["city"] = store["address"]["city"]
    data["state"] = "<MISSING>"
    data["country_code"] = store["address"]["country"]
    data["zip_postal"] = store["address"]["postCode"]
    data["phone"] = store["address"]["phoneNumber"]
    data["latitude"] = store["address"]["latitude"]
    data["longitude"] = store["address"]["longitude"]
    hours = store["tradingPeriods"]
    data["hours_of_operation"] = hoo(hours)

    return data


def fetch_data():
    stores = session.get(api_url).json()

    for store in stores:
        yield parse_json(store)


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
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
