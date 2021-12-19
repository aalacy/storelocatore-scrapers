import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thenottingham_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.thenottingham.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.thenottingham.com/branches/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("span", {"class": "full-details"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("p", {"class": "title"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            address = json.loads(
                r.text.split('<script type="application/ld+json">')[2].split(
                    "</script>"
                )[0]
            )["address"]
            street_address = address["streetAddress"].split(",")[0]
            city = address["addressLocality"]
            state = address["addressRegion"]
            if not state:
                state = MISSING
            zip_postal = address["postalCode"]
            phone = (
                soup.find("li", {"class": "phone"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            hours_of_operation = (
                soup.find("div", {"class": "opening-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Opening hours", "")
            )
            if not city:
                city = location_name.replace("branch", "")
            coords = soup.find("div", {"class": "branch-information-map"})
            latitude = coords["data-lat"]
            longitude = coords["data-lng"]
            country_code = "GB"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
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
