from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ice-canada_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.ice-canada.ca/en/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.ice-canada.ca/en/find-an-office/search/0/48/0/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "small-12 medium-6 large-4 columns"})
        for loc in loclist:
            page_url = "https://www.ice-canada.ca" + loc.find("a")["href"]
            log.info(page_url)
            temp = loc.find("div", {"class": "row store-locator__store__info"})
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("h1").get_text(separator="|", strip=True).split("|")[0]
            )
            address = (
                soup.find("address").get_text(separator="|", strip=True).split("|")
            )
            street_address = address[0]
            temp = address[1].split(",")
            city = temp[0]
            state = temp[1]
            temp = address[2].split(",")
            zip_postal = temp[0].replace("BC ", "")
            country_code = temp[1]
            phone = soup.find("a", {"class": "button big-location-phone"}).text
            hours_of_operation = (
                soup.find("div", {"class": "location-service-points-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Business Hours", "")
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
                latitude=MISSING,
                longitude=MISSING,
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
