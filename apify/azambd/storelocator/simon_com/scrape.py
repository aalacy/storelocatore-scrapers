from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()
DOMAIN = "simon.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

API_URL_ONE = "https://api.simon.com/v1.2/centers/all/index"
API_URL_TWO = "https://api.simon.com/v1.2/mall"

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
    "key": "40A6F8C3-3678-410D-86A5-BAEE2804C8F2",
}


def get_all_malls():
    response = session.get(API_URL_ONE)
    logger.info(f"API ONE Response: {response.status_code}")
    malls_json = response.json()
    mall_ids = {
        mall["mallId"]: "https://www.simon.com/mall/" + mall["urlFriendlyName"]
        for mall in malls_json
    }

    return mall_ids, malls_json


def parse_simon(location):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = location[0]["mallName"]
    data["store_number"] = location[0]["mallId"]

    data["page_url"] = "https://www.simon.com/mall/" + location[0]["urlFriendlyName"]
    data["location_type"] = "Shopping Mall"
    data["street_address"] = location[0]["address"]["street1"]
    data["city"] = location[0]["address"]["city"]
    data["state"] = location[0]["address"]["state"]
    data["country_code"] = location[0]["address"]["country"]
    data["zip_postal"] = location[0]["address"]["zipCode"]
    data["phone"] = location[0]["phones"]["information"]
    data["latitude"] = location[0]["latitude"]
    data["longitude"] = location[0]["longitude"]
    data["raw_address"] = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["state"],
            data["zip_postal"],
            data["country_code"],
        ]
    )
    ooh = []
    for x in location[0]["hours"]:
        if x["isClosed"] == False:
            if x["startDayOfWeek"] == x["endDayOfWeek"]:
                ooh.append(
                    x["startDayOfWeek"] + ": " + x["startTime"] + "-" + x["endTime"]
                )
            else:
                ooh.append(
                    x["startDayOfWeek"]
                    + "-"
                    + x["endDayOfWeek"]
                    + ": "
                    + x["startTime"]
                    + "-"
                    + x["endTime"]
                )
        elif x["isClosed"]:
            if x["startDayOfWeek"] == x["endDayOfWeek"]:
                ooh.append(x["startDayOfWeek"] + ": Closed")
            else:
                ooh.append(x["startDayOfWeek"] + "-" + x["endDayOfWeek"] + ": Closed")

    ooh = ", ".join(ooh)
    data["hours_of_operation"] = ooh

    return data


def parse_not_simon(location):
    data = {}
    data["locator_domain"] = "simon.com"
    data["location_name"] = location["mallName"]
    data["store_number"] = location["mallId"]
    data["page_url"] = "https://www.simon.com/mall/" + location["urlFriendlyName"]
    data["location_type"] = location["propertyType"]
    data["street_address"] = location["address"]["street1"]
    data["city"] = location["address"]["city"]
    data["state"] = location["address"]["state"]
    data["country_code"] = location["address"]["country"]
    data["zip_postal"] = location["address"]["zipCode"]
    data["phone"] = location["mallPhone"]
    raw_address = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["state"],
            data["zip_postal"],
            data["country_code"],
        ]
    )
    data["raw_address"] = (
        raw_address.replace(", ,", ",").replace(",,", ",").replace(", , , ", ",")
    )

    return data


def fetch_data():
    mall_ids, malls_json = get_all_malls()
    missing_ids = []
    for mall in mall_ids.keys():
        querystring = {"mallid": f"{mall}"}
        # Additional API calls to get HOO
        response = session.get(API_URL_TWO, params=querystring, headers=headers)
        logger.info(f"Response API TWO: {response}")
        if response.text == "null":
            missing_ids.append(mall)
            continue

        location = response.json()
        data_simon = parse_simon(location)
        yield data_simon

    for location in malls_json:
        if location["mallId"] in missing_ids:
            data = parse_not_simon(location)
            yield data
        else:
            continue


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
