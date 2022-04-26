from sglogging import sglog
from sgrequests import SgRequests

from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from tenacity import retry, stop_after_attempt
import tenacity


website = "https://www.spectrum.com/locations"
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


@retry(stop=stop_after_attempt(8), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        logger.info(f"HTTP STATUS: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


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
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )

    for z in search:
        api_url = f"https://www.spectrum.com/bin/spectrum/storeLocator?address={z}&miles=500&maxStoresDisplayed=500"
        logger.info(f"Crawling: {api_url}")
        data_json = get_response(api_url)
        if data_json:
            for loc in data_json["response"]["locations"]:
                if "Duplicate" in str(loc):
                    continue

                yield parse_json(loc)


def scrape():
    logger.info(f"Start Crawling {website} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(mapping=["street_address"]),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip_postal"]),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MappingField(mapping=["location_type"]),
        raw_address=sp.MappingField(mapping=["raw_address"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
