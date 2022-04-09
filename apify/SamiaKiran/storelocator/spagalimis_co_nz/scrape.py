from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "spagalimis_co_nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://spagalimis.co.nz/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.spagalimis.co.nz/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "home-cat"})
        for loc in loclist:
            temp = loc.find("a")
            location_name = temp.text
            page_url = temp["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            coords = soup.find("iframe")["src"]
            zip_postal = coords.split("!5")[0].split("+")[-1]
            longitude, latitude = (
                coords.split("!2d", 1)[1].split("!3m", 1)[0].split("!3d")
            )
            phone = soup.select_one("a[href*=tel]").text
            temp = soup.findAll("div", {"class": "wpb_text_column wpb_content_element"})
            address = temp[-2]
            if "Store opening" not in address.text:
                address = temp[-1]
            else:
                address = temp[-2]
            raw_address = address.find("p").text
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            hours_of_operation = (
                soup.find("table")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store opening times:", "")
            )
            latitude, longitude = (
                soup.select_one("iframe[src*=maps]")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d")
            )
            country_code = "NZ"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
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
