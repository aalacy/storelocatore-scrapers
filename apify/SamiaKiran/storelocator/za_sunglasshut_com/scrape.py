from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "za_sunglasshut_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://za.sunglasshut.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://za.sunglasshut.com/store-locator"
        r = session.get(url, headers=headers)
        js_path = r.text.split('<link href="/js/about')[1].split('"')[0]
        api_url = "https://za.sunglasshut.com/js/about" + js_path
        r = session.get(api_url, headers=headers)
        loclist = r.text.split("markers:[{")[1].split("]},E=")[0].split("store_id:")[1:]
        for loc in loclist:
            loc = "store_id:" + loc
            store_number = loc.split('store_id:"')[1].split('"')[0]
            location_name = loc.split('store_title:"')[1].split('"')[0]
            log.info(location_name)
            latitude = loc.split("lat:")[1].split(",")[0]
            longitude = loc.split("lng:")[1].split("}")[0]
            raw_address = loc.split('store_address:"')[1].split('"')[0]
            raw_address = (
                BeautifulSoup(raw_address, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")[1:]
            )
            phone = raw_address[0]
            raw_address = raw_address[-1].replace("{", "")
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "UK"
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
