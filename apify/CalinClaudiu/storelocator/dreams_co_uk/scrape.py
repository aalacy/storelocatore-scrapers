from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Accept": "application/json",
    }

    session = SgRequests()
    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])
    for zipcode in search:
        logzilla.info(f"{zipcode} | remaining: {search.items_remaining()}")
        cont = True
        page = -1
        while cont:
            try:
                page += 1
                results = session.get(
                    "https://www.dreams.co.uk/store-finder?q="
                    + str(zipcode.replace(" ", "+"))
                    + "&page="
                    + str(page)
                    + "&productCode=",
                    headers=headers,
                ).json()
                if results["total"] > 0:
                    for i in results["data"]:
                        try:
                            pair = (i["latitude"], i["longitude"])
                        except Exception:
                            try:
                                pair = (
                                    str(i["url"])
                                    .split("lat=")[1]
                                    .split("&")[0]
                                    .strip(),
                                    str(i["url"]).split("long=")[1].strip(),
                                )
                            except Exception:
                                pair = ""
                        try:
                            search.found_location_at(pair[0], pair[1])
                        except:
                            pass

                        try:
                            i["openings"] = i["openings"]
                        except Exception:
                            i["openings"] = []
                        yield i
            except Exception:
                cont = False

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
            h.append(
                str(
                    str(i["day"])
                    + ": "
                    + str(i["openingTime"])
                    + "-"
                    + str(i["closingTime"])
                )
            )
        if len(h) > 0:
            hours = "; ".join(h)

    return hours


def scrape():
    url = "https://www.dreams.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"],
            is_required=False,
            value_transform=lambda x: "https://www.dreams.co.uk" + x,
        ),
        location_name=sp.MappingField(
            mapping=["displayName"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["line1"],
                ["line2"],
            ],
            multi_mapping_concat_with=", ",
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["town"],
            is_required=False,
            part_of_record_identity=True,
        ),
        state=sp.MissingField(),
        zipcode=sp.MappingField(
            mapping=["postalCode"],
            is_required=False,
            part_of_record_identity=True,
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["openings"],
            raw_value_transform=nice_hours,
        ),
        location_type=sp.MissingField(),
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
