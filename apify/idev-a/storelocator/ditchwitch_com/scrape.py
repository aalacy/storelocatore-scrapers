from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ditchwitch")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.ditchwitch.com"
base_url = "https://www.ditchwitch.com/find-a-dealer"

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=None,
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling zip Code %s..." % zip))
        url = f"https://www.ditchwitch.com/wtgi.php?ajaxPage&ajaxAddress={zip}"
        locations = session.get(url, headers=headers, timeout=15).json()
        if "dealers" in locations:
            total += len(locations["dealers"])
            for loc in locations["dealers"]:
                search.found_location_at(
                    loc["latitude"],
                    loc["longitude"],
                )
                try:
                    mon = "Mon " + loc["mon_open"] + "-" + loc["mon_close"]
                    tue = "; Tue " + loc["tue_open"] + "-" + loc["tue_close"]
                    wed = "; Wed " + loc["wed_open"] + "-" + loc["wed_close"]
                    thu = "; Thu " + loc["thur_open"] + "-" + loc["thur_close"]
                    fri = "; Fri " + loc["fri_open"] + "-" + loc["fri_close"]
                    sat = "; Sat " + loc["sat_open"] + "-" + loc["sat_close"]
                    sun = "; Sun " + loc["sun_open"] + "-" + loc["sun_close"]
                    hours_of_operation = mon + tue + wed + thu + fri + sat + sun
                except:
                    hours_of_operation = "<MISSING>"

                loc["hours_of_operation"] = hours_of_operation
                loc["street_address"] = loc["address1"] + " " + loc.get("address2", "")
                yield loc
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations['dealers'])} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.ConstantField(base_url),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postalcode"],
        ),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MissingField(),
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
