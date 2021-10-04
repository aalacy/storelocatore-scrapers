from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "genkoreanbbq_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.genkoreanbbq.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.genkoreanbbq.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "sqs-block-button-container--center"})
        for loc in loclist:
            if "https://www.genkoreanbbq.com" in loc.find("a")["href"]:
                page_url = loc.find("a")["href"]
            else:
                page_url = "https://www.genkoreanbbq.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "col sqs-col-6 span-6"})[1].findAll(
                "h3"
            )
            address = temp[0].get_text(separator="|", strip=True).split("|")
            if len(address) < 3:
                phone = temp[1].text
            else:
                phone = address[-1]
            if "gmail" in phone:
                phone = address[-2]
            phone = phone.replace("P.", "").replace(" / E.", "")

            address_raw = address[1]
            pa = parse_address_intl(address_raw)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            hours_of_operation = temp[1:]
            hours_of_operation = " ".join(x.text for x in hours_of_operation)
            hours_of_operation = hours_of_operation.replace("OPEN HOUR", "").replace(
                "Store Hours", ""
            )
            hours_of_operation = (
                hours_of_operation.replace("P.", "").replace(phone, "").replace(":", "")
            )
            try:
                country_code = pa.country
                country_code = country_code.strip() if zip_postal else MISSING
            except:
                country_code = "US"
            location_name = city
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
                raw_address=address_raw,
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
