from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Accept": "application/json",
    }

    session = SgRequests()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_search_results=10
    )
    identities = set()
    for lat, long in search:
        logzilla.info(f"{(lat, long)} | remaining: {search.items_remaining()}")
        results = session.get(
            "https://www.nisalocally.co.uk/stores/search?q="
            + str(lat)
            + "%2C"
            + str(long)
            + "&r=2500&l=en",
            headers=headers,
        ).json()
        results = results["response"]
        if results["count"] > 0:
            for i in results["entities"]:
                try:
                    pair = (
                        i["profile"]["geocodedCoordinate"]["lat"],
                        i["profile"]["geocodedCoordinate"]["long"],
                    )
                except Exception:
                    try:
                        pair = (
                            i["profile"]["yextDisplayCoordinate"]["lat"],
                            i["profile"]["yextDisplayCoordinate"]["long"]
                        )
                    except Exception:
                        pair = ""

                try:
                    search.found_location_at(pair[0], pair[1])
                except:
                    pass

                if i["profile"]["c_pagesURL"] not in identities:
                    identities.add(i["profile"]["c_pagesURL"])
                    try:
                        i["profile"]["hours"]["normalHours"] = i["profile"]["hours"][
                            "normalHours"
                        ]
                    except Exception:
                        i["profile"]["hours"] = {}
                        i["profile"]["hours"]["normalHours"] = []
                    try:
                        i["profile"]["geocodedCoordinate"]["lat"] = i["profile"][
                            "geocodedCoordinate"
                        ]["lat"]
                    except Exception:
                        i["profile"]["geocodedCoordinate"] = {}
                        i["profile"]["geocodedCoordinate"]["lat"] = ""
                        i["profile"]["geocodedCoordinate"]["long"] = ""

                    try:
                        i["profile"]["mainPhone"]["number"] = i["profile"]["mainPhone"][
                            "number"
                        ]
                    except Exception:
                        i["profile"]["mainPhone"] = {}
                        i["profile"]["mainPhone"]["number"] = ""

                    try:
                        i["profile"]["meta"]["schemaTypes"] = i["profile"]["meta"][
                            "schemaTypes"
                        ]
                    except Exception:
                        try:
                            i["profile"]["meta"] = i["profile"]["meta"]
                        except Exception:
                            i["profile"]["meta"] = {}
                        i["profile"]["meta"]["schemaTypes"] = []
                    yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def fix_colon(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split(":")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def nice_hours(k):
    hours = "<MISSING>"
    h = []
    if len(k) > 0:
        for i in k:
            if not i["isClosed"]:
                h.append(
                    str(
                        str(i["day"])
                        + ": "
                        + str(i["intervals"][0]["start"])
                        + "-"
                        + str(i["intervals"][0]["end"])
                    )
                )
            elif i["isClosed"]:
                h.append(str(i["day"]) + ": Closed")
        if len(h) > 0:
            hours = "; ".join(h)

    return hours


def scrape():
    url = "https://www.nisalocally.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["profile", "c_pagesURL"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["profile", "name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["profile", "geocodedCoordinate", "lat"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["profile", "geocodedCoordinate", "long"],
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["profile", "address", "line1"],
                ["profile", "address", "line2"],
                ["profile", "address", "line3"],
            ],
            multi_mapping_concat_with=", ",
            is_required=False,
            value_transform=fix_comma,
        ),
        city=sp.MappingField(mapping=["profile", "address", "city"], is_required=False),
        state=sp.MultiMappingField(
            mapping=[
                ["profile", "address", "region"],
                ["profile", "address", "sublocality"],
            ],
            multi_mapping_concat_with=": ",
            value_transform=fix_colon,
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["profile", "address", "postalCode"],
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["profile", "address", "countryCode"], is_required=False
        ),
        phone=sp.MappingField(
            mapping=["profile", "mainPhone", "number"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["profile", "meta", "id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["profile", "hours", "normalHours"],
            raw_value_transform=nice_hours,
        ),
        location_type=sp.MappingField(
            mapping=["profile", "meta", "schemaTypes"],
            raw_value_transform=lambda x: ", ".join(x),
            is_required=False,
        ),
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
