from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "usa2goquickstore_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://usa2goquickstore.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://usa2goquickstore.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.findAll("div", {"class": "fusion-column-content"})
        for loc in loc_block:
            title = loc.find("div", {"class": "fusion-text"}).text.strip()
            if title != "COMING SOON!":
                info = loc.findAll("div", {"class": "fusion-text"})
                title = info[0].text.strip()
                address = info[1].text.strip()
                coords = info[1].find("a")["href"]
                address = address.replace("\n", " ")
                phone = address.split("t:")[1]
                phone = phone.replace("click here for directions", "").strip()
                raw_addr = address.split("t:")[0]
                if coords.find("!1d") != -1:
                    coords = coords.split("!1d")[1].split("!2d")
                    lng = coords[0]
                    lat = coords[1]
                else:
                    lat = MISSING
                    lng = MISSING

                parsed = parser.parse_address_usa(raw_addr)
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
                    page_url=search_url,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
