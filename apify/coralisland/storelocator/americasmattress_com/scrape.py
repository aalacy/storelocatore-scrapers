import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "americasmattress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
}

DOMAIN = "https://www.americasmattress.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.americasmattress.com/gadsden/locations/finderajax"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            location_name = loc["name"]
            phone = loc["phone"]
            street_address = loc["address"]
            if "Coming Soon" in street_address:
                continue
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zipcode"]
            store_number = loc["id"]
            phone = loc["phone"].replace("â€¬", "")
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longtitude"]
            if loc["hours"]:
                h_temp = []
                store_hours = json.loads(loc["hours"])
                for key, hour in list(store_hours.items()):
                    if (
                        "open" in hour
                        and hour["open"] is not None
                        and hour["open"] != ""
                    ):
                        temp = key + " " + hour["open"]
                    if (
                        "close" in hour
                        and hour["close"] is not None
                        and hour["close"] != ""
                    ):
                        temp += "-" + hour["close"]
                    h_temp.append(temp)
                store_hours = ", ".join(h_temp)
            else:
                store_hours = "<MISSING>"
            store_hours = store_hours.replace("sunday 0-0,", "")
            yield SgRecord(
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
                hours_of_operation=store_hours,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
