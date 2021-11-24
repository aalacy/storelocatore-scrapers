from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "cherryblowdrybar_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://cherryblowdrybar.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.cherryblowdrybar.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "two-col-box"})
        for loc in loclist:
            temp = loc.find("h4")
            location_name = temp.text
            page_url = DOMAIN + temp.find("a")["href"]
            log.info(page_url)
            phone = loc.find("a", {"itemprop": "telephone"}).text
            street_address = loc.find("span", {"itemprop": "streetAddress"}).text
            city = loc.find("span", {"itemprop": "addressLocality"}).text
            state = loc.find("span", {"itemprop": "addressRegion"}).text
            zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
            country_code = "US"
            hours_of_operation = (
                loc.find("dl").get_text(separator="|", strip=True).replace("|", " ")
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
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
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
