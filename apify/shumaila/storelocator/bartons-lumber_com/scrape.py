from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bartons-lumber_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.bartons-lumber.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.bartons-lumber.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=location]")
        till_index = len(loclist) / 2 + 1
        till_index = int(till_index)
        loclist = loclist[:till_index]
        for loc in loclist:
            page_url = "https://www.bartons-lumber.com" + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "ResourceItemTitle"}).text
            temp = soup.find("div", {"class": "TwoColumns"}).findAll("p")
            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("HOURS OF OPERATION", "")
            )
            store_number = soup.find("li", {"rel": location_name})["data-id"]
            address = temp[0].get_text(separator="|", strip=True).split("|")
            phone = address[-1]
            if len(address) > 3:
                del address[1]
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
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
                store_number=store_number,
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
