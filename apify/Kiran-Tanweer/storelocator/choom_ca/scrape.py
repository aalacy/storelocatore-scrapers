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
        for idx in range(1, 23):
            if idx == 6:
                continue
            location_type = MISSING
            link = "https://choom.ca/locations/" + str(idx)
            store_id = link.split("/")[-1]
            req = session.get(link, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            title = bs.find("div", {"class": "rl-name is-flex"}).find("h1").text
            log.info(title)
            address = bs.find("div", {"class": "rl-address rl-item"}).findAll("p")
            street = address[0].text
            city = address[1].text
            state = address[2].text
            coords = bs.find("div", {"class": "rl-address rl-item"}).find("a")["href"]
            lat, lng = coords.split("Location/")[1].split(",")
            try:
                hours = bs.find("div", {"class": "rl-open-hours"}).find("ul").text
                hours = re.sub(pattern, " ", hours).strip()
                hours = hours.replace("\n", " ")
            except:
                hours = MISSING
                location_type = "Temporarily Closed"
            try:
                phone = bs.find("div", {"class": "rl-phone"}).text.strip()
            except:
                phone = MISSING
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
                location_type=location_type,
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
