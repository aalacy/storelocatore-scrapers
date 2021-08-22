import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "soelbergsmarket_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://soelbergsmarket.com/"
MISSING = "<MISSING>"


def fetch_data(sgw: SgWriter):
    if True:
        url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackInfoAll&action=storeInfo&website_url=soelbergsmarket.com&_=1626935888845"
        r = session.get(url, headers=headers)
        loclist = r.text.split("jsonpcallbackInfoAll(")[1].split(")")[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["store_name"]
            store_number = loc["store_id"]
            phone = loc["store_phone"]
            hours_of_operation = (
                "Mon-Sat "
                + str(loc["store_hMonOpen"])
                + "-"
                + str(loc["store_hMonClose"])
                + " Sunday "
                + str(loc["store_hSunOpen"])
            )
            street_address = loc["store_address"]
            city = loc["store_city"]
            page_url = "https://soelbergsmarket.com/" + city.replace(" ", "_").lower()
            log.info(page_url)
            zip_postal = loc["store_zip"]
            country_code = "US"
            state = loc["store_state"]
            latitude = loc["store_lat"]
            longitude = loc["store_lng"]
            sgw.write_row(
                SgRecord(
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
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
