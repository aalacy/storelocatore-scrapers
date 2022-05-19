import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "petco_com_mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://petco.com.mx/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.petco.com.mx/petco/en/store-finder"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("select", {"id": "address.region"}).findAll("option")[1:]
        for state_temp in state_list:
            page = 0
            while True:
                state_api = (
                    "https://www.petco.com.mx/petco/en/store-finder?q="
                    + state_temp["value"]
                    + "&page="
                    + str(page)
                )
                page = page + 1
                log.info(state_api)
                try:
                    loclist = session.get(state_api, headers=headers).json()["data"]
                except:
                    break
                for loc in loclist:
                    location_name = strip_accents(loc["displayName"])
                    log.info(location_name)
                    store_number = loc["name"]
                    latitude = loc["latitude"]
                    longitude = loc["longitude"]
                    phone = loc["phone"]
                    street_address = strip_accents(loc["line1"] + " " + loc["line2"])
                    city = strip_accents(loc["town"])
                    state = MISSING
                    zip_postal = loc["postalCode"]
                    hours_of_operation = loc["openings"]
                    hours_of_operation = (
                        str(hours_of_operation)
                        .replace("'", "")
                        .replace("}", "")
                        .replace("{", "")
                    )
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code="MX",
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
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.GeoSpatialId,
            duplicate_streak_failure_factor=1500,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
