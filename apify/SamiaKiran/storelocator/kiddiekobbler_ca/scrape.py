from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "kiddiekobbler_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://kiddiekobbler.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://kiddiekobbler.ca/store-locator/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("table").findAll("tr")[1:]
        for loc in loclist:
            page_url = loc.find("a")["href"]
            loc = loc.findAll("td")
            location_name = loc[1].text
            phone = loc[2].text
            raw_address = loc[3].text
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if "Mall" in raw_address:
                raw_address = (
                    soup.find("tbody")
                    .findAll("tr")[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Address: ", "")
                )
                if raw_address == "Fairview Shopping Center":
                    raw_address = "1800 Sheppard Ave East, Willowdale, Ontario M2J 5A7"
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            try:
                hours_of_operation = (
                    soup.find("table", {"class": "wpseo-opening-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                hours_of_operation = MISSING
            country_code = "CA"
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
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
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
