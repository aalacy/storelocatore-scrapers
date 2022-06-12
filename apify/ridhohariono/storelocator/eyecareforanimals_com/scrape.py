from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "eyecareforanimals.com"
API_URL = "http://www.eyecareforanimals.com/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    payload = {
        "action": "csl_ajax_search",
        "address": "",
        "formdata": "addressInput=",
        "lat": "38.97664042411115",
        "lng": "-94.54224500000001",
        "options[allow_addy_in_url]": "true",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "0",
        "options[initial_radius]": "50000",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax",
        "options[label_phone]": "Phone",
        "options[label_website]": "Website",
        "options[loading_indicator]": "",
        "options[map_center]": "United States",
        "options[map_center_lat]": "37.09024",
        "options[map_center_lng]": "-95.712891",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "/wp-content/plugins/store-locator-le/images/icons/bulb_azure.png",
        "options[map_home_icon]": "/wp-content/plugins/store-locator-le/images/icons/bulb_yellow.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "12",
        "options[zoom_tweak]": "0",
        "radius": "100000",
    }
    data = session.post(API_URL, headers=HEADERS, data=payload).json()
    for row in data["response"]:
        page_url = row["url"]
        info = pull_content(page_url)
        if not info:
            phone = MISSING
            hours_of_operation = MISSING
        else:
            phone = re.sub(
                r"\(\D+\)",
                "",
                info.find("h3", text=re.compile(r"Phone:|Phone"))
                .find_next("p")
                .get_text(strip=True, separator="@@")
                .split("@@")[0]
                .replace("Phone:", ""),
            ).strip()
            hours_of_operation = (
                (
                    info.find("h3", text="Office Hours:")
                    .find_next("p")
                    .get_text(strip=True, separator=",")
                )
                .replace("&nbsp;", "")
                .strip()
            )
        location_name = row["name"].replace("&#039;", "'")
        street_address = (row["address"] + " " + row["address2"]).strip()
        city = row["city"].replace("&#039;", "'")
        state = row["state"]
        zip_postal = row["zip"]
        country_code = "US"
        latitude = row["lat"]
        longitude = row["lng"]
        store_number = row["id"]
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
