from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser
import os

os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"


session = SgRequests()
website = "handypantrystores_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://handypantrystores.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://handypantrystores.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.find("div", {"class": "dmContent"})
        locations = locations.findAll("div", {"data-anim-desktop": "fadeInRight"})
        for loc in range(0, len(locations)):
            locs = locations[loc].findAll("div", {"class": "dmRespCol"})
            for i in range(0, len(locs)):
                store = locs[i]
                if loc == 2:
                    if i == 3:
                        break
                details = store.find("div", {"class": "dmNewParagraph"})
                storeid = details["id"]
                info = store.findAll("div")
                title = info[1].find("span").text
                all_info = info[2]
                address = all_info["addresstodisplay"]
                lat = all_info["data-lat"]
                lng = all_info["data-lng"]
                hours = info[-1].text
                hours = hours.replace("\n", " ").strip()
                address = address.rstrip("United States").strip()
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
                phone = store.find("a")["phone"]

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=search_url,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=storeid,
                    phone=phone,
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
