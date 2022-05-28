from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


DOMAIN = "illinoistitleloansinc.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "authority": "illinoistitleloansinc.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://illinoistitleloansinc.com/title-loan-locations",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "utm_medium=Organic; utm_campaign=; _uc_referrer=direct; _uc_last_referrer=direct; _uc_initial_landing_page=https%3A//illinoistitleloansinc.com/; _ga=GA1.2.1493050633.1643947353; _gid=GA1.2.1825797437.1643947353; utm_source=https://illinoistitleloansinc.com/; _uc_current_session=true; _uc_visits=2; _uetsid=48266ad0856f11ec8cd36582e74c8dff; _uetvid=4826a310856f11ec86c32bf9fea55a21; XSRF-TOKEN=eyJpdiI6InFhUFpJb21JTWFpSmtcL0tTYkZiYlZ3PT0iLCJ2YWx1ZSI6InNUY3JNYVNQb1ptd2RIdzB4VWJjTDhvUlgzVEpyUXZMWW5VT1hPcnFLUHBoNmY5ME1yck1ZR3Y1V1RLUm85N1FSMkVzd0Rsck9YOFA1OVNVQ1BKYnN3PT0iLCJtYWMiOiIzZmVmZjUzNWU5YzRmOWYwZjE3NWRiMTUzZGI5ZmZhNWViM2Y3MmE3OTgyYTYzY2RlM2E4Zjg4NjI5NmUzZDcwIn0%3D; laravel_session=eyJpdiI6InFQWktLUmluU3ptQTQyTFdPVXg2OXc9PSIsInZhbHVlIjoiUXNmdGc5ak1LQUh5bTNpWWhUOVFqQko0bWY4UVRuQmVcL1lvZko1XC9rK2M5SDJaZ2JGc3F5MEhLUmFOYll2QjdicVVJbTFsYzlxQ0pqUG9lam91aVdXZz09IiwibWFjIjoiMjNjMjRiZjMwM2ZlN2NmY2QwYTU3NDQzMTAzNzlhNmZmNGFkOTZjY2ZiYzY3ZGFlYTkzODkzNjJlNTA0ZWMxMyJ9",
}

api_url = "https://illinoistitleloansinc.com/closest-stores?loan_type=all&num=0"

session = SgRequests()


def parse_json(store):
    data = {}
    data["store_number"] = store["store_code"]
    data["page_url"] = "https://illinoistitleloansinc.com/" + store[
        "store_url"
    ].replace("missouri", "illinois").replace("wisconsin", "illinois")
    data["location_name"] = store["business_name"]
    data["location_type"] = "<MISSING>"
    data["street_address"] = store["address_line_1"]
    data["city"] = store["locality"]
    data["state"] = store["administrative_area"]
    data["country_code"] = store["country"]
    data["zip_postal"] = store["postal_code"]
    data["phone"] = store["primary_phone"]
    data["latitude"] = store["latitude"]
    data["longitude"] = store["longitude"]
    data[
        "hours_of_operation"
    ] = "Monday - Friday: 10AM-6PM, Saturday: 10AM-3PM, Sunday: Closed"

    data["raw_address"] = " ".join(
        [
            store["address_line_1"],
            store["locality"],
            store["administrative_area"],
            store["postal_code"],
        ]
    )

    return data


def fetch_data():
    response = session.get(api_url, headers=headers).json()
    jdata = response["locations"]

    for store in jdata:
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
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
