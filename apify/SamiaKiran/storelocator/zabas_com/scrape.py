import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "zabas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://zabas.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://zabas.com/restaurant-locations/"
        r = session.get(url, headers=headers)
        js_url = r.text.split('<script defer src="')[1].split('"></script>')[0]
        r = session.get(js_url, headers=headers)
        loclist = r.text.split('"places":')[1].split(',"styles"')[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            store_number = loc["id"]
            location_name = loc["title"]
            log.info(location_name)
            phone = loc["content"]
            phone = BeautifulSoup(phone, "html.parser")
            phone = phone.find("a").text.replace("+", "")
            raw_address = loc["address"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            latitude = loc["location"]["lat"]
            longitude = loc["location"]["lng"]
            country_code = loc["location"]["country"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
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
