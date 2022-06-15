from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import datetime as dt

DOMAIN = "nike.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

api_url = (
    "https://storeviews-cdn.risedomain-prod.nikecloud.com/store-locations-static.json"
)


def add_hours(time_string, hr):
    the_time = dt.datetime.strptime(time_string, "%I:%M")
    new_time = the_time + dt.timedelta(hours=hr)
    return new_time.strftime("%I:%M")


def pt_hours(store):
    # HOO is in this format "startTime": "11:00", "duration": "PT11H"
    # Its showing the duration and add_hours() fn produce the end_time using the duration

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    hoos = store["operationalDetails"]["hoursOfOperation"]["regularHours"]
    all_hours = []
    for day in days:
        try:
            start_time = hoos[f"{day}"][0]["startTime"]
            duration = hoos[f"{day}"][0]["duration"]
            duration = duration.split("H")[0].replace("PT", "")
            end_time = add_hours(start_time, int(duration))
            all_hours.append(f"{day}:{start_time} - {end_time}")
        except:
            all_hours.append(f"{day}:Closed")

    hoo = ", ".join(all_hours)

    return hoo


def update_location_name(location_name):
    if "nike" in location_name.lower() and "-" in location_name:
        return location_name.split("-")[0].strip()

    if "nike" not in location_name.lower():
        if location_name.upper() == location_name:
            return "NIKE " + location_name
        else:
            return "Nike " + location_name
    return location_name


def parse_json(store):
    data = {}
    data["locator_domain"] = DOMAIN
    data["store_number"] = store["storeNumber"]
    data["page_url"] = "https://www.nike.com/retail/s/" + store["slug"]
    data["location_name"] = update_location_name(store["name"])
    data["location_type"] = store["facilityType"]
    data["street_address"] = (
        store["address"]["address1"]
        + " "
        + store["address"]["address2"]
        + " "
        + store["address"]["address3"]
    )
    data["city"] = store["address"]["city"]
    data["state"] = store["address"]["state"]
    data["country_code"] = store["address"]["iso2Country"]
    data["zip_postal"] = store["address"]["postalCode"]
    data["phone"] = store["phone"]
    data["latitude"] = store["coordinates"]["latitude"]
    data["longitude"] = store["coordinates"]["longitude"]
    data["hours_of_operation"] = pt_hours(store)

    data["raw_address"] = (
        data["street_address"]
        + " "
        + data["city"]
        + " "
        + data["state"]
        + " "
        + data["zip_postal"]
    )

    return data


def fetch_data():
    for store in data["stores"]:
        i = data["stores"][f"{store}"]
        yield parse_json(i)


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
    with SgRequests() as session:
        data = session.get(api_url).json()

    scrape()
