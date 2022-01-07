import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "basefashion_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://basefashion.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://basefashion.co.uk/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "column main"}).findAll(
            "div", {"data-appearance": "full-width"}
        )[1:]
        for loc in loclist:
            temp = loc.findAll("p")
            phone = loc.select_one("a[href*=tel]").text
            location_name = temp[0].find("strong").text
            log.info(location_name)
            coords = loc.find("a", string=re.compile("Directions"))["href"]
            if "@" in coords:
                coords = coords.split("@")[1].split(",")
                latitude = coords[0]
                longitude = coords[1]
            else:
                latitude, longitude = coords.split("/")[-1].split(",")
            raw_address = " ".join(x.text for x in temp[1:])

            hours_of_operation = loc.findAll("div", {"class": "opening-hours"})[
                -1
            ].get_text(separator="|", strip=True)
            hours_of_operation = hours_of_operation.replace("|", " ").replace(
                "OPENING HOURS", ""
            )
            hours_of_operation = (
                re.sub(pattern, "\n", hours_of_operation).replace("\n", " ").strip()
            )
            raw_address = (
                raw_address.split("Directions")[0].replace(phone, "").replace("T:", "")
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
            country_code = "UK"
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
                latitude=latitude,
                longitude=longitude,
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
