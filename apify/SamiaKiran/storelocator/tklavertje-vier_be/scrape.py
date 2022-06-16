from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tklavertje-vier_be"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.tklavertje-vier.be"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.tklavertje-vier.be/service/winkels/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "span6"})
        for loc in loclist:
            try:
                location_name = loc.find("h2").text
            except:
                continue
            log.info(location_name)
            raw_address = (
                loc.find("address")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .split("T:")
            )
            if loc.find("a", {"class", "btn"}):
                coords = (
                    loc.find("a", {"class", "btn"})["href"].split("@")[1].split(",")
                )
                latitude = coords[0]
                longitude = coords[1]
            else:
                latitude = MISSING
                longitude = MISSING

            hours_of_operation = (
                loc.find("ul", {"class": "openingsuren"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Do 26/5 gesloten (feestdag)", "")
                .replace("'s middags steeds doorlopend open", "")
            )
            phone = raw_address[-1]
            raw_address = raw_address[0]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "BE"
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
