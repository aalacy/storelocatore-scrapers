from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

session = SgRequests()
website = "dicos_com_cn"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://dicos.com.cn"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://www.dicos.com.cn/store.html"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var DealerArray = ")[1].split("}];")[0]
        loclist = json.loads(loclist + "}]")
        for loc in loclist:
            location_name = loc["dealername"]
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            street_address = loc["address"]
            city = loc["city"]
            state = loc["province"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            country_code = "CN"
            raw_address = (
                street_address + " " + loc["district"] + " " + city + " " + state
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=MISSING,
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
