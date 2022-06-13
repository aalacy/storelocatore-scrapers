import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "jackwills_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.jackwills.com"
MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    if True:
        url = "https://www.jackwills.com/stores/search?countryName=United%20Kingdom&countryCode=GB&lat=0&long=0&sd=500"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"id": "StoreFinderResultsListing"}).findAll(
            "div", {"class": "StoreFinderStore"}
        )
        for link in linklist:
            latitude = link["data-latitude"]
            longitude = link["data-longitude"]
            store_number = link["data-store-code"]
            page_url = link.find("a", {"class": "StoreFinderResultsDetailsLink"})[
                "href"
            ].replace("..", "https://www.jackwills.com")
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loc = soup.find("div", {"id": "StoreDetailsContainer"})
            location_name = loc.find("h1").text.strip()
            temp = (
                loc.find("div", {"id": "StoreDetailsText"})
                .findAll("div", {"class": "StoreFinderList"})[2]
                .text.strip()
            )
            temp = re.sub(pattern, "\n", temp).split("\n")
            if len(temp) > 3:
                street_address = temp[0] + " " + temp[1]
                city = temp[2]
                zip_postal = temp[3]
            else:
                street_address = temp[0]
                city = temp[1]
                zip_postal = temp[2]
            state = MISSING
            country_code = "UK"
            hourlist = loc.findAll("meta", {"itemprop": "openingHours"})
            hours_of_operation = ""
            for hour in hourlist:
                hours_of_operation = hours_of_operation + " " + hour["content"]
            phone = loc.find("span", {"itemprop": "telephone"}).text
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
