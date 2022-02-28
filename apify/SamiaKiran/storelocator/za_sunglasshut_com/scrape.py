from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "za_sunglasshut_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://za.sunglasshut.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://za.sunglasshut.com/index.php?route=extension/module/wk_store_locater/setter"
        r = session.get(url, headers=headers)
        loclist = r.text.split("~")
        for loc in loclist[:-1]:
            soup = BeautifulSoup(loc, "html.parser")
            phone = soup.find("a").text
            _tmp = loc.split("!")
            store_number = _tmp.pop(0)
            longitude = _tmp.pop(0)
            latitude = _tmp.pop(0)
            location_name = _tmp.pop(0)
            log.info(location_name)
            raw_address = _tmp.pop(0)
            raw_address = raw_address.replace("Tel. Number:", "").replace(phone, "")

            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://za.sunglasshut.com/index.php?route=wk_store_locator/wk_store_locator",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=MISSING,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
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
