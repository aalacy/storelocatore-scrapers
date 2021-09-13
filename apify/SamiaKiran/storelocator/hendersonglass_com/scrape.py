from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "hendersonglass_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://hendersonglass.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://hendersonglass.com/locations/"
        r = session.get(url, headers=headers, timeout=180)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "locationsCol"})
        for loc in loclist:
            try:
                coords = loc.find("a")["href"].split("@")[1].split(",")
                latitude = coords[0]
                longitude = coords[1]
            except:
                latitude = MISSING
                longitude = MISSING
            loc = loc.get_text(separator="|", strip=True).split("|")
            location_name = loc[0]
            log.info(location_name)
            if len(loc) < 5:
                street_address = MISSING
                zip_postal = MISSING
                city = MISSING
                state = MISSING
                country_code = MISSING
                phone = loc[1].replace("Phone:", "")
            else:
                address = loc[1]
                phone = loc[2].replace("Phone:", "")
                raw_address = address.replace(",", " ")
                # Parse the address
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                hours_of_operation = MISSING
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
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
