from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("officedepot_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.officedepot.com/"

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
    MAX_DISTANCE = 550
    for zip_code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % zip_code))
        url = (
            'https://storelocator.officedepot.com/ajax?&xml_request=<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>500</limit><geolocs><geoloc><addressline>'
            + str(zip_code)
            + "</addressline></geoloc></geolocs><searchradius>"
            + str(MAX_DISTANCE)
            + "</searchradius>"
        )
        locations = bs(
            session.get(url, headers=headers, timeout=15).text, "lxml"
        ).find_all("poi")
        total += len(locations)
        for _ in locations:
            store = {}
            store["location_name"] = _.find("seoid").text
            store["street_address"] = _.find("address1").text
            store["city"] = _.find("city").text
            store["state"] = _.find("state").text
            store["zip_postal"] = _.find("postalcode").text
            store["country_code"] = _.find("country").text
            store["phone"] = _.find("phone").text or "<MISSING>"
            store["store_number"] = _.find("clientkey").text
            store["location_type"] = _.find("icon").text
            store["latitude"] = _.find("latitude").text
            store["longitude"] = _.find("longitude").text
            search.found_location_at(
                store["latitude"],
                store["longitude"],
            )
            store["hours_of_operation"] = (
                "mon:"
                + " "
                + str(_.find("mon").text)
                + "; tues:"
                + " "
                + str(_.find("tues").text)
                + "; wed:"
                + " "
                + str(_.find("wed").text)
                + "; thur:"
                + " "
                + str(_.find("thur").text)
                + "; fri:"
                + " "
                + str(_.find("fri").text)
                + "; sat:"
                + " "
                + str(_.find("sat").text)
                + "; sun:"
                + " "
                + str(_.find("sun").text)
            )
            store["page_url"] = (
                "https://www.officedepot.com/storelocator/"
                + str(store["state"].lower())
                + "/"
                + str(store["city"].replace(" ", "-").lower())
                + "/office-depot-"
                + str(store["store_number"])
                + "/"
            )
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
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
            mapping=["zip_postal"],
        ),
        country_code=sp.MappingField(
            mapping=["country_code"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MappingField(
            mapping=["location_type"],
        ),
        store_number=sp.MappingField(
            mapping=["store_number"],
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
