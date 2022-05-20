from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "smilingmoosedeli.com"
LOCATION_URL = "https://smilingmoosedeli.com/locations/"
API_URL = "https://smilingmoosedeli.com/smd-wp/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    payloads = {
        "action": "csl_ajax_onload",
        "address": "",
        "formdata": "addressInput=",
        "lat": "37.09024",
        "lng": "-95.712891",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "base",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "1",
        "options[initial_radius]": "1200",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Catering:",
        "options[label_phone]": "Phone:",
        "options[label_website]": "Facebook",
        "options[loading_indicator]": "",
        "options[map_center]": "Denver,CO",
        "options[map_center_lat]": "37.09024",
        "options[map_center_lng]": "-95.712891",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "http://smilingmoosedeli.com/smd-wp/wp-content/plugins/store-locator-le/images/icons/bulb_red.png",
        "options[map_home_icon]": "http://smilingmoosedeli.com/smd-wp/wp-content/plugins/store-locator-le/images/icons/flag_azure.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "0",
        "options[zoom_tweak]": "0",
        "radius": "1200",
    }
    data = session.post(API_URL, headers=HEADERS, data=payloads).json()
    for row in data["response"]:
        location_name = row["name"].strip()
        if "Coming Soon" in location_name:
            continue
        street_address = (row["address"] + ", " + row["address2"]).strip().rstrip(",")
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        phone = row["phone"]
        country_code = "US" if row["country"] == "United States" else row["country"]
        if state == "North Dakota":
            country_code = "US"
        store_number = row["id"]
        hours_of_operation = (
            row["hours"].replace("\r\n", ",").replace("Mon-Fri -", "Mon-Fri:").strip()
        )
        latitude = row["lat"]
        longitude = row["lng"]
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
