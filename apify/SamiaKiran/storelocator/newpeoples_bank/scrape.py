from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "newpeoples_bank"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.newpeoples.bank/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.newpeoples.bank/Locations"
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        loclist = str(soup.findAll("table")[5]).split("<h2>")[1:]
        for loc in loclist:
            loc = "<h2>" + loc
            loc = BeautifulSoup(loc, "html.parser")
            location_name = loc.find("h2").text
            log.info(location_name)
            temp = loc.findAll("p")[1:]
            raw_address = (
                temp[0]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Address", "")
            )

            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "US"
            phone = temp[1].find("a").text
            hours_of_operation = (
                loc.find("table")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Hours Lobby Hours", "")
            )
            hours_of_operation = hours_of_operation.split("Drive Thru")[0]
            if "ITM Hours*" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("ITM Hours*")[0]
            if "S Boone" in city:
                city = city.replace("S", "")
            street_address = street_address + " S"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
