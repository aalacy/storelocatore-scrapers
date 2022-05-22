from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "dutch_love"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Cookie": "_landing_page=%2Fpages%2Fstore-list; _orig_referrer=; _s=79a23675-cf45-48d4-94bc-e4be5673cae6; _shopify_s=79a23675-cf45-48d4-94bc-e4be5673cae6; _shopify_y=316ba6f8-0ad2-4471-a2bf-c02ef4123d56; _y=316ba6f8-0ad2-4471-a2bf-c02ef4123d56; secure_customer_sig="
}

DOMAIN = "https://dutch.love/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://dutch.love/pages/store-list"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.findAll("div", {"class": "store-list-page__store-details"})
        links = soup.findAll("div", {"class": "image-with-text__image"})
        for loc, link in zip(loc_block, links):
            title = loc.find("h3").text
            address = (
                loc.find("div", {"class": "store-list-page__store-details--address"})
                .find("p")
                .text
            )
            hours = (
                loc.find("div", {"class": "opening-hours t--header-navigation"})
                .find("p")
                .text
            )
            link = "https://dutch.love" + link.find("a")["href"]
            address = address.strip()
            city = loc.find("h4", {"class": "t--header-navigation font-size--sm"}).text
            req = session.get(link, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            phones = bs.findAll("a", {"class", "remove-link"})
            for ph in phones:
                checker = str(ph)
                if checker.find("tel") != -1:
                    ph = ph.text
                    phone = ph
            parsed = parser.parse_address_intl(address)
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
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="CAN",
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
