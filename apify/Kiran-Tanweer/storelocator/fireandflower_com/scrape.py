from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "fireandflower_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://fireandflower.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://fireandflower.com/stores"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.findAll("div", {"class": "locations-page--shop"})
        for loc in loc_block:
            link = loc.find("a")["href"]
            link = "https://fireandflower.com/" + link
            store = session.get(link, headers=headers)
            bs = BeautifulSoup(store.text, "html.parser")
            title = bs.find("h1", {"class": "m-0"}).text
            address = bs.find("div", {"class": "location-page--address"}).find("p").text
            contact = bs.find("div", {"class": "location-page--contact"}).find("a").text
            hours = (
                bs.find("div", {"class": "location-page--hours"})
                .find("ul")
                .text.strip()
            )
            hours = hours.replace("\n", " ").strip()
            coords = bs.find("div", {"class": "location-page--interactions"}).find("a")[
                "href"
            ]
            lat, lng = coords.split("Location/")[1].split(",")
            address = address.strip()
            address = address.split("\n")
            street = address[0]
            city, state = address[1].split(",")
            pcode = address[2]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="CAN",
                store_number=MISSING,
                phone=contact.strip(),
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
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
