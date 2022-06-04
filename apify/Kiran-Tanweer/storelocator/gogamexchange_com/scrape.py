from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser

session = SgRequests()
website = "gogamexchange_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
DOMAIN = "https://www.gogamexchange.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        search_url = "https://www.gogamexchange.com/find-a-store/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        state = soup.findAll("div", {"class": "state"})
        for locations in state:
            stores = locations.findAll("div", {"class": "store"})
            for store in stores:
                store_id = store["data-id"]
                lat = store["data-lat"]
                lng = store["data-lng"]
                title = store.find("h3").text
                address = store.find("p", {"class": "address"}).text
                phone = store.find("a", {"class": "store-phone"}).text
                link = store.find("a", {"class": "link"})["href"]
                req = session.get(link, headers=headers)
                bs = BeautifulSoup(req.text, "html.parser")
                hours = bs.find("div", {"class": "ld-hours"}).find("p").text
                address = address.replace("#9", "#9 ").strip()
                address = address.strip()
                parsed = parser.parse_address_usa(address)
                street1 = (
                    parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
                )
                street = (
                    (street1 + ", " + parsed.street_address_2)
                    if parsed.street_address_2
                    else street1
                )
                city = parsed.city if parsed.city else "<MISSING>"
                state = parsed.state if parsed.state else "<MISSING>"
                pcode = parsed.postcode if parsed.postcode else "<MISSING>"

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link.strip(),
                    location_name=title.strip(),
                    street_address=street.strip(),
                    city=city,
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=store_id,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours.strip(),
                    raw_address=address.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
