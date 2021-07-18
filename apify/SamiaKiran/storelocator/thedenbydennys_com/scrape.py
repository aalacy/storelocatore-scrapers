from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

session = SgRequests()
website = "thedenbydennys_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://thedenbydennys.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://thedenbydennys.com/assets/js/main.js"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var locations = ")[1].split("];")[0]
        loclist = loclist.split("{'map_link'")[1:]
        for loc in loclist:
            loc = loc.replace("<p>", " ").replace("<br>", " ").replace("</p>", " ")
            location_name = loc.split("'name': '")[1].split(",")[0]
            location_name = location_name.replace("'", "")
            log.info(location_name)
            raw_address = loc.split("'address': '")[1].split("'}")[0]
            raw_address = raw_address.replace("Memorial Student Center", "").replace(
                "Second floor", ""
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
