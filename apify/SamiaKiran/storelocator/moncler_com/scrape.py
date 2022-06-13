import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "moncler_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.moncler.com/en-us/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.moncler.com/on/demandware.store/Sites-MonclerUS-Site/en_US/StoresApi-FindAll"
        loclist = session.get(url, headers=headers).json()["stores"]
        for loc in loclist:
            store_number = loc["ID"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            location_name = loc["name"]
            phone = loc["phone"]
            hours_of_operation = ""
            try:
                street_address = loc["address1"] + " " + loc["address2"]
            except:
                try:
                    street_address = loc["address1"]
                except:
                    street_address == loc["address2"]
            street_address = strip_accents(street_address)
            city = strip_accents(loc["city"])
            try:
                state = strip_accents(loc["stateCode"])
            except:
                state = MISSING
            try:
                zip_postal = strip_accents(loc["postalCode"])
            except:
                zip_postal = MISSING
            if state.isdigit():
                state = MISSING
            if len(state) < 2:
                state = MISSING
            raw_address = strip_accents(
                street_address + " " + city + " " + state + " " + zip_postal
            )
            raw_address = raw_address.replace(MISSING, "")
            country_code = loc["countryCode"]["value"]
            page_url = "https://www.moncler.com/en-us/storelocator/" + loc["slug"]
            log.info(page_url)
            hour_list = loc["storeHours"]
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation + " " + hour["day"] + " " + hour["text"]
                )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
