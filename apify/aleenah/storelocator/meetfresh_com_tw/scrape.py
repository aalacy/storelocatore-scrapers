from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "meetfresh_com_tw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://meetfresh.com.tw/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://www.meetfresh.com.tw/API/Location"
        country_list = session.get(url, headers=headers).json()["cn"]
        log.info("Fetching the data from API, will take atleast 40 seconds...")
        for country in country_list:
            area_wrap = country["area_wrap"]
            for area in range(len(area_wrap)):
                loclist = country["store"][str(area)]
                if not loclist:
                    continue
                for loc in loclist:
                    location_name = loc["storename"]
                    if "coming soon" in location_name:
                        continue
                    store_number = loc["id"]
                    log.info(location_name)
                    phone = loc["tel"]
                    raw_address = loc["address"]
                    if not raw_address:
                        continue
                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street_address = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    zip_postal = zip_postal.strip() if zip_postal else MISSING
                    country_code = loc["area"]
                    hours_of_operation = loc["subTitle"]
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
                        latitude=MISSING,
                        longitude=MISSING,
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
