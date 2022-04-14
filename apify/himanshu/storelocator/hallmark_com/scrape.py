import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "hallmark_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.hallmark.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://maps.hallmark.com/api/getAsyncLocations?template=search&level=search&radius=100000000&search=USA&limit=5000"
    r = session.get(url, headers=headers).json()
    log.info("Getting " + str(len(r["markers"])) + " links..(Approx. 1hr..)")
    for x in r["markers"]:
        soup = BeautifulSoup(x["info"], "lxml")
        div_data = json.loads(soup.text)
        location_name = div_data["location_name"].split("-Curbside")[0].strip()
        street_address = div_data["address_1"]
        city = div_data["city"]
        state = div_data["region"]
        zip_postal = div_data["post_code"]
        country_code = div_data["country"]
        phone = div_data["local_phone"]
        store_number = x["locationId"]
        location_type = "<MISSING>"
        latitude = x["lat"]
        longitude = x["lng"]
        page_url = div_data["url"]
        log.info(page_url)
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        hours_of_operation = ""
        if soup1.find("div", {"class": "hours"}) is not None:
            sentence = soup1.find("div", {"class": "hours"}).text.strip()
            pattern = re.compile(r"\s+")
            hours_of_operation = re.sub(pattern, " ", sentence)
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
            phone=phone.strip(),
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
