import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "missoulafm_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://missoulafm.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackInfoAll&action=storeInfo&website_url=missoulafm.com"
        loclist = session.get(url, headers=headers)
        loclist = loclist.text.split("jsonpcallbackInfoAll(")[1].split(")")[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            store_number = loc["store_id"]
            location_name = loc["store_name"]
            page_url = (
                "https://missoulafm.com/" + location_name.split("-")[1].strip().lower()
            )
            log.info(page_url)
            phone = loc["store_phone"]
            street_address = loc["store_address"]
            city = loc["store_city"]
            state = loc["store_state"]
            zip_postal = loc["store_zip"]
            country_code = "US"
            latitude = loc["store_lat"]
            longitude = loc["store_lng"]
            hours_of_operation = (
                "Mon-Sat: "
                + loc["store_hMonOpen"]
                + "-"
                + loc["store_hMonClose"]
                + " "
                + "Sun: "
                + loc["store_hSunOpen"]
                + "-"
                + loc["store_hSunClose"]
            )
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
