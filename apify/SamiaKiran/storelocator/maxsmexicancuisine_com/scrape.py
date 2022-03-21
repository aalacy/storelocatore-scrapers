import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "maxsmexicancuisine_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.maxsmexicancuisine.com"
MISSING = SgRecord.MISSING


def parse_geo(url):
    lon = re.findall(r"\,(--?[\d\.]*)", url)[0]
    lat = re.findall(r"\@(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    if True:
        url = "https://www.maxsmexicancuisine.com/contact"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"data-testid": "richTextElement"})
        for loc in loclist:
            if loc.find("h5") is None:
                continue
            location_name = loc.find("h5").text
            log.info(location_name)
            temp = loc.findAll("p")
            hours_of_operation = " ".join(hour.text for hour in temp[0:4])
            street_address = temp[4].text
            coords = temp[4].find("a")["href"]
            latitude, longitude = parse_geo(coords)
            phone = temp[6].text
            temp = temp[5].text.split()
            city = temp[0].replace(",", "")
            state = temp[1]
            zip_postal = temp[2]
            country_code = "US"
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
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
