from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "guzmanygomez_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://guzmanygomez.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.guzmanygomez.com/all-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=all-location]")
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("h2")
                .get_text(separator="|", strip=True)
                .replace("|", "")
                .split("– Drive")[0]
            )
            address = soup.find("div", {"class": "order_location"}).findAll("span")
            street_address = address[0].text
            city = address[1].text
            state = address[2].text
            zip_postal = address[3].text
            temp = soup.findAll("table", {"class": "order_location"})
            hours_of_operation = (
                temp[1].get_text(separator="|", strip=True).replace("|", " ")
            )
            phone = (
                temp[0]
                .findAll("td")[1]
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            country_code = "US"
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
