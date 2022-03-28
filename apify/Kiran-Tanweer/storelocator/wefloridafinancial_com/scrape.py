from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import re
from sgscrape import sgpostal as parser


session = SgRequests()
website = "wefloridafinancial_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Cookie": "ca50283db89d1012d5eb1bed1089b3e8=187081e6159ba516cf2e8e9e6e844f67"
}

DOMAIN = "https://www.wefloridafinancial.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        url = "https://www.wefloridafinancial.com/belong/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.findAll("a", {"class": "sppb-btn sppb-btn-link"})
        for link in div:
            url = "https://www.wefloridafinancial.com" + link["href"]
            r = session.get(url, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            title = bs.find("h1", {"class": "sppb-addon-title"}).text
            address = (
                bs.findAll("div", {"class": "sppb-addon-content"})[1]
                .find("h5")
                .find("a")["href"]
            )
            address = (
                address.split("/place/")[1].split("/@")[0].replace("+", " ").strip()
            )
            coords = (
                bs.findAll("div", {"class": "sppb-addon-content"})[1]
                .find("h5")
                .find("a")["href"]
            )
            coords = coords.split("/@")[1].split(",1")[0].strip()
            lat, lng = coords.split(",")
            hours = (
                bs.findAll("div", {"class": "sppb-addon-content"})[2]
                .text.replace("\n", " ")
                .strip()
            )
            hours = hours.split("DRIVE-UP WINDOW HOURS")[0]
            if hours.find("HOURS") != -1:
                hours = hours.split("HOURS")[1].strip()
            elif hours.find("Branch Closed") != -1:
                continue
            hours = re.sub(pattern, " ", hours)
            hours = re.sub(cleanr, " ", hours)

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
                page_url=url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
                raw_address=address.strip(),
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
