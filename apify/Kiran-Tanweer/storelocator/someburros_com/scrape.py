from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "someburros_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.someburros.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        divname = []
        search_url = "https://someburros.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.find("article", {"id": "post-9"}).findAll("div")
        for d in loc_block:
            name = d["class"]
            if len(name) == 3:
                divname.append(name[0] + " " + name[1] + " " + name[2])
        for loc in divname:
            loc_block = soup.find("article", {"id": "post-9"}).find(
                "div", {"class": loc}
            )
            title = loc_block.find("h3").text
            address = loc_block.find("p").text
            if len(loc_block.findAll("p")) == 4:
                hours = loc_block.findAll("p")[3].text
            else:
                hours = loc_block.findAll("p")[2].text
            address = address.split("\n")
            phone = address[-1]
            address = address[0] + " " + address[1]
            phone = phone.replace("TACO (", "")
            phone = phone.replace(")", "").strip()
            hours = hours.replace("\n", " ")
            hours = hours.replace(" Order online", "").strip()
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
                page_url="https://someburros.com/locations/",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
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
