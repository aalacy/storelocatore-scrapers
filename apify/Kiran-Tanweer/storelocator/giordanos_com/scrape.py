from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape import sgpostal as parser

session = SgRequests()
website = "giordanos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://giordanos.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://giordanos.com/all-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "locationsection"}).findAll("a")
        for link in linklist:
            page = "https://giordanos.com" + link["href"]
            p = session.get(page, headers=headers)
            soup = BeautifulSoup(p.text, "html.parser")
            address = soup.find("div", {"class": "address"}).text
            address = address.replace(",", "").strip()
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

            phone = soup.find("div", {"class": "phone my-2"}).text.strip()

            hours = soup.find("div", {"class": "hours"}).text.strip()
            hours = hours.replace("\n", ", ")

            title = soup.find("h1", {"class": "text-center"}).text.strip()

            coords = soup.find("body").findAll("script")
            if len(coords) == 11:
                coords = coords[2]
            else:
                coords = coords[0]
            coords = str(coords)
            coords = coords.split("center: {")[1].split("}")[0]
            lat = coords.split("lat: ")[1].split(",")[0]
            lng = coords.split("lng: ")[1]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page,
                location_name=title.strip(),
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=lat.strip(),
                longitude=lng.strip(),
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
