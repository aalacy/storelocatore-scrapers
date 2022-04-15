from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


DOMAIN = "bywoops.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "authority": "bywoops.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://bywoops.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://bywoops.com/locations/cool-springs-franklin-mall/",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6",
}


def parse_json(store):
    data = {}

    data["store_number"] = store["ID"]
    data["page_url"] = "https://bywoops.com/locations/" + "-".join(
        store["post_title"].split("! ")[1].lower().split(" ")
    )
    data["location_name"] = store["post_title"]
    data["location_type"] = store["terms"][0]["name"]
    data["street_address"] = " ".join(
        [store["meta"]["store_address"], store["meta"]["store_address_2"]]
    )
    data["city"] = store["meta"]["store_city"]
    data["state"] = store["meta"]["store_state"]
    data["country_code"] = "US"
    data["zip_postal"] = store["meta"]["store_zip"]
    data["phone"] = store["meta"]["store_phone"]
    data["latitude"] = store["meta"]["store_latitude"]
    data["longitude"] = store["meta"]["store_longitude"]

    tc = store["meta"]["store_show_as_closed"].strip()

    if "Coming" in str(data["location_type"]) and tc == "1":
        data["location_type"] = "Temporarily Closed"
        logger.info(f'{ data["location_name"]} => {data["location_type"]}')

    try:
        data["hours_of_operation"] = ", ".join(
            [
                day["store_opening_day"].title()
                + ": "
                + day["store_opening_open"]
                + "-"
                + day["store_opening_close"]
                for day in store["meta"]["store_opening_hours"]
            ]
        )
    except Exception as e:
        logger.info(f"ERROR OOH: {e}")
        data["hours_of_operation"] = "<MISSING>"

    data["raw_address"] = ", ".join(
        [
            store["meta"]["store_address"],
            store["meta"]["store_address_2"],
            store["meta"]["store_city"],
            store["meta"]["store_state"],
            store["meta"]["store_zip"],
            data["country_code"],
        ]
    )
    return data


def fetch_data():
    session = SgRequests()
    api_url = "https://bywoops.com/api"

    payload = {
        "m": "GET",
        "r": "/woops/v1/stores/nearby?latitude=45.4901977&longitude=9.2271889&limit=500&virtual=true",
    }

    response = session.post(api_url, json=payload, headers=headers)
    data_json = response.json()
    for store in data_json["data"]:
        yield parse_json(store)


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
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
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
