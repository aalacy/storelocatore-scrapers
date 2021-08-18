from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "beefsteakveggies_com "
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.beefsteakveggies.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.beefsteakveggies.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "SubMenu-1"}).findAll("li")[1:]
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if "https://www.beefsteakveggies.com" not in page_url:
                page_url = "https://www.beefsteakveggies.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if "Opening" in soup.find("div", {"class": "col-md-6"}).text:
                continue
            temp = soup.find("div", {"class": "col-md-6"})
            location_name = temp.find("h2").text
            temp = temp.findAll("p")
            address = (
                temp[0]
                .find("a", {"data-bb-track-category": "Address"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            try:
                phone = (
                    temp[0].find("a", {"data-bb-track-category": "Phone Number"}).text
                )
            except:
                phone = MISSING
            location_type = MISSING
            hours_of_operation = temp[1].text
            if "Temporarily Closed" in hours_of_operation:
                location_type = "Temporarily Closed"
                hours_of_operation = MISSING
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
                location_type=location_type,
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
