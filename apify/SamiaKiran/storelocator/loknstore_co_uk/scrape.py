import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "loknstore_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.loknstore.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.loknstore.co.uk/self-storage/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "select", {"class": "form--select__component js-select-store"}
        ).findAll("option")
        for loc in loclist[1:]:
            page_url = loc["value"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "Open-Soon.png" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                "LoknStore " + soup.find("span", {"class": "store__name"}).text
            )

            try:
                temp = json.loads(
                    r.text.split('<script type="application/ld+json">')[1].split(
                        "</script>"
                    )[0]
                )
                latitude = temp["latitude"]
                longitude = temp["longitude"]
            except:
                latitude = MISSING
                longitude = MISSING

            hours_of_operation = (
                soup.find("div", {"class": "opening__hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("(Call for information)", "")
                .replace("TBC", "")
            )
            phone = soup.find("p", {"class": "store__number"}).text
            raw_address = soup.find("p", {"class": "store__address__container"}).text
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "GB"
            if "CURRENTLY CLOSED" in hours_of_operation:
                location_type = "Temporarily Closed"
            else:
                location_type = MISSING
            if "Open hours : Closed" in hours_of_operation:
                continue
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
                location_type=location_type,
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
