import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "leightons_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.leightons.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.leightons.co.uk/branches"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "branch-list"}).findAll("li")
        for loc in loclist:
            temp = loc.find("a")
            page_url = temp["href"]
            location_name = temp.get_text(separator="|", strip=True).replace("|", " ")
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = r.text.split('"address":')[2].split("}")[0]
            address = json.loads(address + "}")
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            country_code = "GB"
            latitude = r.text.split(' "latitude": "')[1].split('"')[0]
            longitude = r.text.split(' "longitude": "')[1].split('"')[0]
            phone = (
                soup.find("div", {"class": "branch-aside__contact"})
                .find("a")["href"]
                .replace("tel:", "")
            )
            hours_of_operation = (
                soup.find("div", {"class": "branch-aside__opening-times"})
                .find("ul")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
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
