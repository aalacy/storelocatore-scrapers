from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("canadiantire")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.canadiantire.ca"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=None,
    max_search_results=None,
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        url = f"https://api-triangle.canadiantire.ca/dss/services/v4/stores?lang=en&radius=10000&maxCount=1000&lat={lat}&lng={lng}&storeType=store"
        locations = session.get(url, headers=headers, timeout=15).json()
        total += len(locations)
        if "errors" in locations:
            continue
        for loc in locations:
            search.found_location_at(
                loc["storeLatitude"],
                loc["storeLongitude"],
            )
            try:
                hours_obj = loc["workingHours"]["general"]
                mon = (
                    "Mon " + hours_obj["monOpenTime"] + "-" + hours_obj["monCloseTime"]
                )
                tue = (
                    " Tue " + hours_obj["tueOpenTime"] + "-" + hours_obj["tueCloseTime"]
                )
                wed = (
                    " Wed " + hours_obj["wedOpenTime"] + "-" + hours_obj["wedCloseTime"]
                )
                thu = (
                    " Thu " + hours_obj["thuOpenTime"] + "-" + hours_obj["thuCloseTime"]
                )
                fri = (
                    " Fri " + hours_obj["friOpenTime"] + "-" + hours_obj["friCloseTime"]
                )
                sat = (
                    " Sat " + hours_obj["satOpenTime"] + "-" + hours_obj["satCloseTime"]
                )
                sun = (
                    " Sun " + hours_obj["sunOpenTime"] + "-" + hours_obj["sunCloseTime"]
                )
                hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            except:
                hours_of_operation = ""

            loc[
                "page_url"
            ] = f"https://www.canadiantire.ca/en/store-details/{loc['storeProvince']}/{loc['storeCrxNodeName']}.store.html"
            loc["hours_of_operation"] = hours_of_operation
            loc["street_address"] = loc["storeAddress1"] + " " + loc["storeAddress2"]
            yield loc
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        if locations:
            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["storeName"],
        ),
        store_number=sp.MappingField(
            mapping=["storeNumber"],
        ),
        latitude=sp.MappingField(
            mapping=["storeLatitude"],
        ),
        longitude=sp.MappingField(
            mapping=["storeLongitude"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["storeCityName"],
        ),
        state=sp.MappingField(
            mapping=["storeProvince"],
        ),
        zipcode=sp.MappingField(
            mapping=["storePostalCode"],
        ),
        country_code=sp.ConstantField("CA"),
        phone=sp.MappingField(
            mapping=["storeTelephone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MappingField(
            mapping=["storeType"],
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
