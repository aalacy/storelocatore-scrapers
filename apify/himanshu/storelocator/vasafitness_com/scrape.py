from lxml import etree
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "vasafitness_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://vasafitness.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    start_url = "https://vasafitness.com/locations/"
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = []
    all_states = dom.xpath('//div[@class="list-item"]/a/@href')
    for state_url in all_states:
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "View Location")]/@href')
    for page_url in all_locations:
        log.info(page_url)
        loc_response = session.get(page_url)
        soup = BeautifulSoup(loc_response.text, "html.parser")
        location_name = soup.find("h1").text
        try:
            phone = soup.select_one("a[href*=tel]").text
        except:
            phone = MISSING
        address = soup.find("div", {"class": "loc-address"}).text.split(",")
        street_address = address[0]
        city = address[1]
        address = address[2].split()
        state = address[0]
        zip_postal = address[1]
        country_code = "USA"
        latitude = MISSING
        longitude = MISSING
        try:
            hours_of_operation = (
                soup.find("div", {"class": "hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            hours_of_operation = MISSING
        coords = soup.find("div", {"class": "marker"})
        latitude = coords["data-latt"]
        longitude = coords["data-lngg"]
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
