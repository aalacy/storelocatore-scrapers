import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "pizzabolis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.pizzabolis.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.pizzabolis.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", string=re.compile("Directions"))
        for link in linklist:
            page_url = link["href"]
            if "#" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "locations" not in str(r.url):
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            loc = r.text.split("var $location = [")[1].split(",];var", 1)[0]
            latitude = loc.split("lat ", 1)[1].split(":", 1)[1].split(",", 1)[0].strip()
            longitude = (
                loc.split(",lng ", 1)[1].split(":", 1)[1].split(",", 1)[0].strip()
            )
            phone = (
                loc.split("phone ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            location_name = (
                loc.split("name ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )

            store_number = (
                loc.split("id ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            street_address = (
                loc.split("street ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            city = (
                loc.split("city ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            state = (
                loc.split("state ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            zip_postal = (
                loc.split("zip ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            country_code = "US"
            hourlist = soup.find("div", {"id": "hours"}).find("ul").findAll("li")
            hours_of_operation = ""
            for hour in hourlist:
                day = hour.find("span", {"class": "day"}).text
                open_time = hour.find("span", {"class": "open"}).text
                close_time = hour.find("span", {"class": "close"}).text
                hours_of_operation = (
                    hours_of_operation + day + " " + open_time + "-" + close_time + " "
                )
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
