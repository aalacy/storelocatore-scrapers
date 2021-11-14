from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "simplyfresh_info"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


payload = "action=csl_ajax_search&address=&formdata=addressInput%3D&lat=52.22334817473196&lng=-1.6088485000000041&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=10000&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=B48+7LA&options%5Bmap_center_lat%5D=52.352035&options%5Bmap_center_lng%5D=-1.959403&options%5Bmap_domain%5D=maps.google.co.uk&options%5Bmap_end_icon%5D=https%3A%2F%2Fsimplyfresh.info%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fsimplyfresh.info%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbox_yellow_home.png&options%5Bmap_region%5D=uk&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=0&options%5Bzoom_tweak%5D=0&radius=500"
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "referer": "https://www.simplyfresh.info/",
}


DOMAIN = "https://www.simplyfresh.info/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://simplyfresh.info/wp-admin/admin-ajax.php"
        loclist = session.post(url, headers=headers, data=payload).json()["response"]
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.simplyfresh.info/find-a-store/",
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
                hours_of_operation=MISSING,
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
