from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "originalbuscemis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

payload = "action=csl_ajax_onload&address=&formdata=addressInput%3D&lat=42.565576&lng=-83.127351&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=42.565576&options%5Bmap_center_lng%5D=-83.127351&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Foriginalbuscemis.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=https%3A%2F%2Foriginalbuscemis.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_clear_red.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius="
headers = {
    "authority": "originalbuscemis.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://originalbuscemis.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://originalbuscemis.com/locations/",
    "accept-language": "en-US,en;q=0.9",
}


DOMAIN = "https://originalbuscemis.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://originalbuscemis.com/wp-admin/admin-ajax.php"
        loclist = session.post(url, headers=headers, data=payload).json()["response"]
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            store_number = loc["id"]
            phone = loc["phone"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            country_code = "US"
            hours_of_operation = loc["hours"].replace("\n", " ")
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
