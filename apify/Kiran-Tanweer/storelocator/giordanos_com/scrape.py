from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "giordanos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://giordanos.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://giordanos.com/all-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "locationsection"}).findAll("a")
        for link in linklist:
            page = "https://giordanos.com" + link["href"]
            log.info(page)
            p = session.get(page, headers=headers)
            soup = BeautifulSoup(p.text, "html.parser")
            address = soup.find("div", {"class": "address"}).text
            address = address.replace(",", "").strip()
            raw_address = address.strip()
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            phone = soup.find("div", {"class": "phone my-2"}).text.strip()

            hours = soup.find("div", {"class": "hours"}).text.strip()
            hours = hours.replace("\n", ", ")

            title = soup.find("h1", {"class": "text-center"}).text.strip()

            lat = p.text.split("lat: ")[1].split(",")[0]
            lng = p.text.split("lng: ")[1].split("}")[0]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page,
                location_name=title.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=lat.strip(),
                longitude=lng.strip(),
                hours_of_operation=hours,
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
