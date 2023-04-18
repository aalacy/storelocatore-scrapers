from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dpd")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dpd.co.uk"
base_url = "https://www.dpd.co.uk/esgServer/reference/postcode/{}"
url = "https://www.dpd.co.uk/esgServer/depot/{}"

search = DynamicZipSearch(
    country_codes=[SearchableCountries.BRITAIN],
)


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % zip))
        obj = session.get(base_url.format(zip), headers=_headers).json()["obj"]
        if obj:
            store = session.get(url.format(obj["depotCode"]), headers=_headers).json()[
                "obj"
            ]
            if store:
                hours = []
                for hh in store.get("openTime", []):
                    times = "closed"
                    if not hh.get("closed"):
                        times = f"{hh['startTime']}-{hh['endTime']}"
                    if hh["startTime"]:
                        hours.append(f"{hr_obj[str(hh['weekDay'])]}: {times}")
                store["latitude"] = store["addressPoint"]["latitude"]
                store["longitude"] = store["addressPoint"]["longitude"]
                store["street"] = (
                    store["address"]["street"] + " " + store["address"]["town"]
                )
                store["city"] = store["address"]["organisation"]
                store["zipcode"] = store["address"]["postCode"]
                store["phone"] = store["telephone"]
                store["hours"] = "; ".join(hours) or "<MISSING>"
                yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"| progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["city"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MissingField(),
        zipcode=sp.MappingField(
            mapping=["zipcode"],
        ),
        country_code=sp.ConstantField("UK"),
        phone=sp.MappingField(
            mapping=["telephone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["depotTypeName"],
        ),
        store_number=sp.MappingField(
            mapping=["depotCode"],
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
