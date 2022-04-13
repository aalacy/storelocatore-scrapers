from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://locations.huddlehouse.com/search?q="
    headers = {}
    headers["accept"] = "application/json"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    session = SgRequests()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_search_results=10,
        max_search_distance_miles=10,
    )
    identities = set()
    maxZ = search.items_remaining()
    total = 0
    for zipcode in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0

        son = session.get(url + zipcode + "", headers=headers).json()

        for i in son["locations"]:

            search.found_location_at(i["loc"]["latitude"], i["loc"]["longitude"])
            if (
                str(
                    str(i["loc"]["latitude"])
                    + str(i["loc"]["longitude"])
                    + str(i["loc"]["id"])
                )
                not in identities
            ):
                identities.add(
                    str(
                        str(i["loc"]["latitude"])
                        + str(i["loc"]["longitude"])
                        + str(i["loc"]["id"])
                    )
                )
                found += 1
                yield i

        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{zipcode} | found: {found} | total: {total} | progress: {progress}"
        )

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def human_hours(x):
    hours = []
    for i in x["days"]:
        string = str(i["day"]).capitalize() + ": "
        for j in i["intervals"]:
            string = (
                string
                + str(str(int(j["start"]) / 100) + ":" + str(int(j["start"]) % 100))
                + "-"
                + str(str(int(j["end"]) / 100) + ":" + str(int(j["end"]) % 100))
                + " "
            )
    if len(hours) > 1:
        return "; ".join(hours)
    else:
        return "<MISSING>"


def scrape():
    url = "https://locations.huddlehouse.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"],
            value_transform=lambda x: url + x,
        ),
        location_name=sp.MappingField(
            mapping=["loc", "name"],
        ),
        latitude=sp.MappingField(
            mapping=["loc", "latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["loc", "longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["loc", "address1"], ["loc", "address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["loc", "city"],
        ),
        state=sp.MappingField(
            mapping=["loc", "state"],
        ),
        zipcode=sp.MappingField(
            mapping=["loc", "postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["loc", "country"],
        ),
        phone=sp.MappingField(
            mapping=["loc", "phone"],
        ),
        store_number=sp.MappingField(
            mapping=["loc", "id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["loc", "hours"], raw_value_transform=human_hours
        ),
        location_type=sp.MappingField(
            mapping=["loc", "products"], raw_value_transform=lambda x: "; ".join(x)
        ),  # handle coming soon
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
