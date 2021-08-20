from lxml import etree
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "promartialarts.com"
BASE_URL = "https://promartialarts.com"
API_ENDPOINT = "https://promartialarts.com/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()


def fetch_data():
    data = "action=csl_ajax_onload&address=&formdata=addressInput%3D&lat=37.09024&lng=-95.712891&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fnewtempwebsite.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fpromartialarts.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fflag_azure.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius="
    r = session.post(API_ENDPOINT, headers=HEADERS, data=data).json()

    for idx, val in enumerate(r["response"]):
        page_url = val["url"]
        location_name = val["name"].strip().replace("&#039;s", " ")
        street_address = val["address"].strip()
        city = val["city"].strip()
        state = val["state"].strip()
        zip_postal = val["zip"].strip()
        store_number = "<MISSING>"
        country_code = val["country"].strip()
        phone = val["phone"].replace("(KICK)", "").strip()
        if not phone:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//button[@class="call"]/text()')[0]
        location_type = "promartialarts"
        latitude = val["lat"].strip()
        longitude = val["lng"].strip()
        hours_of_operation = val["hours"].replace("&amp;", " ").strip()
        raw_address = f"{street_address}, {city}, {state}, {zip_postal}"
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
