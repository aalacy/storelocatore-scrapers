from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "admabiocenters_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.admabiocenters.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.admabiocenters.com/find-a-center"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "location-tabs"}).findAll("li")
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            if "coming-soon" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("h2").get_text(separator="|", strip=True).replace("|", " ")
            )
            temp = soup.findAll("div", {"class": "flex-item"})
            address = temp[2].find("p").get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            phone = temp[4].find("p").text
            hours_of_operation = (
                temp[6].find("p").get_text(separator="|", strip=True).replace("|", " ")
            )
            longitude, latitude = (
                soup.select_one("iframe[src*=maps]")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d")
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
