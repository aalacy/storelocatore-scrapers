import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "therubyslippercafe_net"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://therubyslippercafe.net"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.therubyslippercafe.net/locations/"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("locations: [")[1]
            .split('team": []}}]')[0]
            .split('"team": []}},')
        )
        for loc in loclist:
            location_type = MISSING
            loc = loc.split(', "store_locator_custom_button_text')[0]
            loc = json.loads(loc + "}")
            hours_of_operation = loc["hours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")
            if "Coming in 2022" in hours_of_operation:
                continue
            if "temporarily closed" in hours_of_operation:
                hours_of_operation = MISSING
                location_type = "Temporarily Closed"
            hours_of_operation = hours_of_operation.split("We do not accept")[0]
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            location_name = loc["name"]
            store_number = loc["id"]
            phone = loc["phone_number"]
            street_address = loc["street"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
