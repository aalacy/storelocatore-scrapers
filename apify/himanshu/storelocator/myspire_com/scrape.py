from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "myspire_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}

session = SgRequests()
DOMAIN = "https://myspire.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://myspire.com/Branches-ATMs"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    page_list = soup.find("div", {"class": "PagerNumberArea"}).findAll("a")[-2].text
    for page in range(1, int(page_list) + 1):
        locator_domain = DOMAIN + "branches-atms?page=" + str(page)
        log.info(locator_domain)
        r = session.get(locator_domain, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        loclist = soup.findAll("div", {"class": "row result"})
        for loc in loclist:
            location_name = (
                loc.find("h3", {"class": "locationheadingTXT"}).find("a").text
            )
            log.info(location_name)
            address = (
                loc.find("p", {"class": "locationsHoursTXTaddress"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            phone = loc.select_one("a[href*=tel]").text
            latitude, longitude = (
                loc.find("a")["onclick"].split("Window(")[1].split(")")[0].split(",")
            )
            hours_of_operation = (
                loc.find("p", {"class": "locationsHoursTXT"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
