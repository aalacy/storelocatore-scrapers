from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "visionlab.es"
LOCATION_URL = "https://www.visionlab.es/opticas/"
API_URL = "https://www.visionlab.es/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    payload = {
        "action": "csl_ajax_search",
        "address": "",
        "formdata": "addressInput=",
        "lat": "40.463667",
        "lng": "-3.74922",
        "options[distance_unit]": "km",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "0",
        "options[initial_radius]": "",
        "options[label_directions]": "Ver en Google Maps",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax",
        "options[label_phone]": "Teléfono",
        "options[label_website]": "Website",
        "options[loading_indicator]": "",
        "options[map_center]": "Spain",
        "options[map_center_lat]": "40.463667",
        "options[map_center_lng]": "-3.74922",
        "options[map_domain]": "maps.google.es",
        "options[map_end_icon]": "https://www.visionlab.es/wp-content/plugins/store-locator-le/images/icons/bulb_red.png",
        "options[map_home_icon]": "https://www.visionlab.es/wp-content/plugins/store-locator-le/images/icons/blank.png",
        "options[map_region]": "es",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "5",
        "options[zoom_tweak]": "0",
        "radius": "500",
    }
    data = session.post(API_URL, headers=HEADERS, data=payload).json()
    for row in data["response"]:
        location_name = row["name"].strip()
        street_address = (row["address"] + " " + row["address2"]).strip()
        city = row["city"]
        state = row["state"].strip() or MISSING
        zip_postal = row["zip"]
        phone = row["phone"]
        country_code = "ES"
        hours_of_operation = re.sub(
            r"^,|,Sábados Julio y Agosto:.*|,\(.*\)",
            "",
            row["hours"]
            .replace("\r\n", ",")
            .replace(" ", " ")
            .strip()
            .rstrip(",")
            .rstrip("."),
        )
        store_number = row["id"]
        location_type = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
