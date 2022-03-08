from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import re


session = SgRequests()
website = "choom_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://choom.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        search_url = "https://choom.ca/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.findAll("a", {"class": "is-choomblue"})
        for loc in loc_block:
            link = loc["href"]
            store_id = link.split("/")[-1]
            req = session.get(link, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            title = bs.find("div", {"class": "rl-name is-flex"}).find("h1").text
            address = bs.find("div", {"class": "rl-address rl-item"}).findAll("p")
            street = address[0].text
            city = address[1].text
            state = address[2].text
            coords = bs.find("div", {"class": "rl-address rl-item"}).find("a")["href"]
            lat, lng = coords.split("Location/")[1].split(",")
            hours = bs.find("div", {"class": "rl-open-hours"}).find("ul").text
            hours = re.sub(pattern, " ", hours).strip()
            hours = hours.replace("\n", " ")
            phone = bs.find("div", {"class": "rl-phone rl-item"}).text.strip()
            pcode = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="CAN",
                store_number=store_id,
                phone=phone,
                location_type=MISSING,
                latitude=lat.strip(),
                longitude=lng.strip(),
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
