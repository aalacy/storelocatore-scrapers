from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "btonefitness_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.btonefitness.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.btonefitness.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"role": "listitem"})
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            r = session.get(page_url, headers=headers)
            if "Opening Summer 2022" in r.text:
                continue
            log.info(page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("span", {"class": "studio-name"}).text
            street_address = soup.find("span", {"class": "studio-address"}).text
            address = (
                soup.select_one("a[href*=maps]")["href"]
                .split("&destination=")[1]
                .split("&destination_")[0]
                .split()
            )
            zip_postal = address[-1]
            state = address[-2]
            city = address[-3].replace(",", "")
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
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
