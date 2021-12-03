from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "arbys_mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://arbys.mx/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.arbys.mx/ubicacion"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "item info"})
        for loc in loclist:

            hour_list = loc.find("div", {"class": "horario"}).findAll("p")[1:]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = hours_of_operation + " " + hour.text
            temp_address = loc.find("div", {"class": "direccion"}).findAll("p")
            raw_address = ""
            for address in temp_address[1:-1]:
                raw_address = raw_address + " " + address.text
            coords = temp_address[-1].find("a")["href"].split("!3d", 1)[1].split("!4d")
            latitude = coords[0]
            longitude = coords[1]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            log.info(street_address)
            country_code = "MX"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=MISSING,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
