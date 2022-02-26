from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

session = SgRequests()
DOMAIN = "unitedsupermarkets.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

apiurl = "https://www.unitedsupermarkets.com/RS.Relationshop/StoreLocation/GetAllStoresPosition"
payload = "__RequestVerificationToken=0ITuGohSF2U4Dbvp6YtEySO7hALqnpaEZr0epcOd8-8Fd3r9B32md64KQ_9Q_lfVVskiCjOcNuRXaAdaI12wUNX9Ufs1"


def parse_json(store):
    data = {}
    data["locator_domain"] = "unitedsupermarkets.com"
    data["location_name"] = store["StoreName"]
    data["store_number"] = store["StoreID"]

    data["page_url"] = (
        "https://www.unitedsupermarkets.com/rs/StoreLocator?id=" + f"{store['StoreID']}"
    )
    data["location_type"] = "Supermarket"
    data["street_address"] = store["Address1"]
    data["city"] = store["City"]
    data["state"] = store["State"]
    data["country_code"] = "US"
    data["zip_postal"] = store["Zipcode"]
    data["phone"] = store["PhoneNumber"]
    data["latitude"] = store["Latitude"]
    data["longitude"] = store["Longitude"]
    if data["longitude"] != 0 and data["street_address"] != "Address":

        data["hours_of_operation"] = store["StoreHours"]
        if data["hours_of_operation"] is not None:
            data["hours_of_operation"] = store["StoreHours"].replace(";", ",")
        else:
            data["hours_of_operation"] = "<MISSING>"
        try:
            data["raw_address"] = ", ".join(
                [
                    data["street_address"],
                    data["city"],
                    data["state"],
                    data["zip_postal"],
                    data["country_code"],
                ]
            )
        except Exception as e:
            logger.info(f"Missing Address {e}")
            data["raw_address"] = "<MISSING>"

        return data


def fetch_data():
    stores = session.post(apiurl, headers=headers, data=payload).json()
    for store in stores:
        i = parse_json(store)
        if i is None:
            continue
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
