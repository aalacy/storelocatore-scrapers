from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "hueyburger_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://hueyburger.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://hueyburger.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("section", {"class": "elementor-top-section"})
        for loc in loclist:
            if "Phone:" in loc.text:
                store_number = loc["data-id"]
                temp = loc.find("h4").find("a")
                page_url = temp["href"]
                log.info(page_url)
                location_name = temp.text
                city = location_name
                temp = loc.findAll("p")
                phone = temp[0].text.replace("Phone:", "")
                hours_of_operation = (
                    temp[-1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("HOURS:", "")
                )
                address = loc.find("iframe")["title"]
                address = address.split(",")
                zip_postal = address[-1]
                street_address = " ".join(x for x in address[:-1])
                state = MISSING
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
