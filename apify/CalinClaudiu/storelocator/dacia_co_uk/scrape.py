from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    url = "https://www.dacia.co.uk/find-a-dealer/find-a-dealer-listing.data?page="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    page = 0
    son = session.get(url + str(page), headers=headers).json()
    totalpages = son["content"]["editorialZone"]["slice54vb"]["dealers"]["totalPages"]
    for i in son["content"]["editorialZone"]["slice54vb"]["dealers"]["data"]:
        yield i
    while page <= totalpages:
        son = session.get(url + str(page), headers=headers).json()
        for i in son["content"]["editorialZone"]["slice54vb"]["dealers"]["data"]:
            try:
                i["geolocalization"]["lat"] = i["geolocalization"]["lat"]
            except Exception:
                i["geolocalization"] = {}
                i["geolocalization"]["lat"] = ""
                i["geolocalization"]["lon"] = ""

            try:
                i["telephone"]["value"] = i["telephone"]["value"]
            except Exception:
                i["telephone"] = {}
                i["telephone"]["value"] = ""

            yield i
        page += 1

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
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


def nice_hours(k):
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    h = []
    hours = "<MISSING>"
    for i in k:
        h.append(str(days[i["day"]] + ": " + i["open"] + "-" + i["close"]))
    if len(h) > 0:
        hours = "; ".join(h)
    return hours


def scrape():
    url = "https://www.dacia.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"], part_of_record_identity=True, is_required=False
        ),
        latitude=sp.MappingField(
            mapping=["geolocalization", "lat"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["geolocalization", "lon"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["extendedAddress"],
            part_of_record_identity=True,
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["locality"], part_of_record_identity=True, is_required=False
        ),
        state=sp.MissingField(),
        zipcode=sp.MappingField(
            mapping=["postalCode"],
            is_required=False,
            part_of_record_identity=True,
        ),
        country_code=sp.MappingField(
            mapping=["country"],
            part_of_record_identity=True,
        ),
        phone=sp.MappingField(
            mapping=["telephone", "value"],
            is_required=False,
        ),
        store_number=sp.MappingField(mapping=["dealerId"]),
        hours_of_operation=sp.MissingField(),
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
