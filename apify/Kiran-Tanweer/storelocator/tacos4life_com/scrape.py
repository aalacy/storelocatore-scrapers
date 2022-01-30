import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "tacos4life_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tacos4life.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://tacos4life.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loclist = soup.findAll("div", {"class": "location-item w-dyn-item"})
    for loc in loclist:
        page_url = "https://www.tacos4life.com" + loc.find("a")["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp = r.text.split("locationData =")[2].split(" 'mealsCounter': 0")[0]
        location_name = temp.split("'name': '")[1].split("'")[0]
        location_name = html.unescape(location_name)
        street_address = temp.split("'street': '")[1].split("'")[0]
        city = temp.split(" 'city': '")[1].split("'")[0]
        city = html.unescape(city)
        state = temp.split("  'abbreviation': '")[1].split("'")[0]
        zip_postal = temp.split("'zip': '")[1].split("'")[0]
        country_code = "US"
        phone = temp.split("'phone': '")[1].split("'")[0]
        hours_of_operation = (
            soup.findAll("div", {"class": "location-info-item"})[1]
            .find("div", {"class": "text-center"})
            .text.replace("\n", " ")
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
