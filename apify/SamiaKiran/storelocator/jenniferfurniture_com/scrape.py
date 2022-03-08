import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "jenniferfurniture_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.jenniferfurniture.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.jenniferfurniture.com/pages/store-locator"
        r = session.get(url, headers=headers)
        api_url = (
            r.text.split("var urls = ")[1]
            .split("]")[0]
            .split('","')[-2]
            .replace("\\/", "/")
        )
        r = session.get(api_url, headers=headers)
        loclist = (
            r.text.split('"locationsRaw":"')[1]
            .split('","app_url"')[0]
            .replace('\\"', '"')
        )
        loclist = json.loads(loclist)
        for loc in loclist:
            page_url = loc["web"].replace("\\/", "/")
            log.info(page_url)
            store_number = str(loc["id"])
            location_name = loc["name"]
            phone = loc["phone"]
            street_address = loc["address"].split(",")[1]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal"]
            country_code = loc["country"]
            latitude = str(loc["lat"])
            longitude = str(loc["lng"])
            hours_of_operation = loc["schedule"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = (
                hours_of_operation.get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("\\r", "")
            )
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
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
