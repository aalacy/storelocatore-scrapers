import json
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.simple_scraper_pipeline import *
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

DOMAIN = "spectrum.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def parse_json(loc):
    data = {}
    data["store_number"] = loc["id"]
    data["latitude"] = loc["yextDisplayLat"]
    data["longitude"] = loc["yextDisplayLng"]
    data["page_url"] = loc["displayWebsiteUrl"]
    data["location_type"] = "Store"
    data["location_name"] = loc["locationName"] + " - " + loc["address"]

    if "Closed" in data["location_name"]:
        data["location_type"] = "Closed"
        data["location_name"] = data["location_name"].replace("- Closed", "")

    data["street_address"] = loc["address"]
    data["city"] = loc["city"]
    data["state"] = loc["state"]
    data["country_code"] = loc["countryCode"]
    data["zip_postal"] = loc["zip"]
    try:
        data["phone"] = loc["phone"]
    except Exception as e:
        logger.info(f"Error PHONE: {e}")
        data["phone"] = "<MISSING>"
    try:
        if "additionalHoursText" in list(loc.keys()):
            data[
                "hours_of_operation"
            ] = "Sun:Closed, Mon:Closed, Tue:Closed, Wed:Closed, Thu:Closed, Fri:Closed, Sat:Closed"
        elif loc["hours"] == "":
            data[
                "hours_of_operation"
            ] = "Sun:Closed, Mon:Closed, Tue:Closed, Wed:Closed, Thu:Closed, Fri:Closed, Sat:Closed"
        else:
            dict_week = {
                "1": "Sun",
                "2": "Mon",
                "3": "Tue",
                "4": "Wed",
                "5": "Thu",
                "6": "Fri",
                "7": "Sat",
            }

            ooh = []
            for day in loc["hours"].split(","):
                decoded = dict_week[day[0]] + ":" + day[2:7] + "-" + day[8:]
                ooh.append(decoded)
            ooh = ", ".join(ooh)
            data["hours_of_operation"] = ooh
    except Exception as e:
        logger.info(f"ERROR OOH {e}")
        data["hours_of_operation"] = "<MISSING>"

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
    search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

    for z in search:
        api_url = f"https://www.spectrum.com/bin/spectrum/storeLocator?address={z}&miles=500&maxStoresDisplayed=500"
        logger.info(f"Crawling: {api_url}")
        response = session.get(api_url, headers=headers)
        data_json = response.json()

        for loc in data_json["response"]["locations"]:
            if "Duplicate" in str(loc):
                continue

            yield parse_json(loc)


def scrape():

    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(DOMAIN),
        page_url=MappingField(mapping=["page_url"]),
        location_name=MappingField(mapping=["location_name"]),
        latitude=MappingField(mapping=["latitude"]),
        longitude=MappingField(mapping=["longitude"]),
        street_address=MappingField(mapping=["street_address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["zip_postal"]),
        country_code=MappingField(mapping=["country_code"]),
        phone=MappingField(mapping=["phone"]),
        store_number=MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=MappingField(mapping=["hours_of_operation"]),
        location_type=MappingField(mapping=["location_type"]),
        raw_address=MappingField(mapping=["raw_address"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
