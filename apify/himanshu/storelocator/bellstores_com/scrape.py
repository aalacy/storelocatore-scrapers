import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "bellstores_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bellstores.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://bellstores.com/home/locations"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    scripts = soup.find_all("script")
    for script in scripts:
        if "var locations" in script.text:
            location_list = json.loads(
                script.text.split("var locations = ")[1].split("]")[0] + "]"
            )
            for loc in location_list:
                location_name = loc["Name"]
                log.info(location_name)
                phone = loc["PhoneNumber"]
                try:
                    street_address = loc["Address1"] + " " + loc["Address2"]
                except:
                    street_address = loc["Address1"]
                log.info(street_address)
                city = loc["City"]
                state = loc["State"]
                zip_postal = loc["Zip"]
                country_code = "US"
                latitude = loc["Latitude"]
                longitude = loc["Longitude"]
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
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
