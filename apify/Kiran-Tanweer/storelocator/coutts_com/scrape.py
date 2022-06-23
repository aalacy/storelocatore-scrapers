from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "coutts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://coutts.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://www.coutts.com/locations.html"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_block = soup.find("div", {"id": "883394888"}).findAll("a")
    for loc in loc_block:
        title = loc.text
        try:
            link = "https://www.coutts.com" + loc["href"]
        except KeyError:
            continue
        stores_req = session.get(link, headers=headers)
        bs = BeautifulSoup(stores_req.text, "html.parser")
        try:
            address = bs.findAll(
                "div",
                {"class": "richText component section grid_6 prefix_3 even appear"},
            )[-1]
        except IndexError:
            address = bs.findAll(
                "div",
                {
                    "class": "richText component section grid_6 prefix_3 richtext_0_copy appear"
                },
            )[-1]
        address = address.find("p").text
        try:
            telephone = bs.findAll(
                "div",
                {
                    "class": "richText component section grid_6 prefix_3 alpha even appear"
                },
            )
            phone = telephone[0]
            hours = telephone[-1]
            if link == "https://www.coutts.com/locations/birmingham.html":
                telephone = bs.findAll(
                    "div",
                    {
                        "class": "richText component section grid_6 prefix_3 alpha even appear"
                    },
                )[1]
                phone = telephone
        except IndexError:
            telephone = bs.findAll(
                "div",
                {
                    "class": "richText component section grid_6 prefix_3 alpha richtext_1923073318 locations-richText appear"
                },
            )
            phone = telephone[0]
            hours = bs.find(
                "div",
                {
                    "class": "richText component section grid_6 prefix_3 alpha richtext_1923073318_ locations-richText appear"
                },
            )

        phone = phone.find("p").text
        hours = hours.find("p").text
        hours = hours.replace("Reception ", "").strip()
        hours = hours.replace("  ", " ")

        lat = bs.find("meta", {"name": "latitude"})["content"]
        lng = bs.find("meta", {"name": "longitude"})["content"]

        parsed = parser.parse_address_intl(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
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
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code="UK",
            store_number=MISSING,
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
