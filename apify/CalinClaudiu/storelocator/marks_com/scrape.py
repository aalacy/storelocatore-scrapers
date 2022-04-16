from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        expected_search_radius_miles=15,
        max_search_results=0,
    )
    with SgRequests(dont_retry_status_codes=set([424])) as session:
        for zipcode in search:
            url = f"https://api.marks.com/hy/v1/marks/storelocators/near?code=&productIds=&count=60&location={zipcode[0]},{zipcode[1]}"  # noqa
            try:
                son = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
            except Exception as e:
                if "424" in str(e) or "403" in str(e):
                    continue
                else:
                    logzilla.info(f"{e}")
                    raise
            if son:
                if son["storeLocatorPageData"]["results"]:
                    for i in son["storeLocatorPageData"]["results"]:
                        try:
                            search.found_location_at(
                                i["geoPoint"]["latitude"], i["geoPoint"]["longitude"]
                            )
                        except Exception:
                            pass
                        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = (
        x.replace("None", "")
        .replace("null", "")
        .replace("Null", "")
        .replace("none", "")
        .replace("  ", " ")
    )
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://www.marks.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["name"],
            value_transform=lambda x: "https://www.marks.com/en/stores/" + str(x),
        ),
        location_name=sp.MappingField(
            mapping=["displayName"],
        ),
        latitude=sp.MappingField(
            mapping=["geoPoint", "latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["geoPoint", "longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["address", "town"],
        ),
        state=sp.MappingField(
            mapping=["address", "region", "isocode"],
        ),
        zipcode=sp.MappingField(
            mapping=["address", "postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["address", "region", "countryIso"],
        ),
        phone=sp.MappingField(
            mapping=["address", "phone"],
        ),
        store_number=sp.MappingField(
            mapping=["name"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["workingHours"],
            value_transform=lambda x: x.replace("\n", "; ")
            .replace("\r", "; ")
            .replace("\t", "; ")
            .replace("; ; ; ", "; ")
            .replace("; ; ", "; "),
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["address", "formattedAddress"],
        ),
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
