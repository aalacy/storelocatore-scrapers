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
website = "costcutter_ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.costcutter.ie/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.costcutter.ie/find-your-local-costcutter/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_list = soup.find("ul", {"class": "page-numbers"}).findAll("li")[:-1]
        for page in page_list:
            url = (
                "https://www.costcutter.ie/find-your-local-costcutter/?pagenum="
                + page.text
            )
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = r.text.split('"markers_info":')[1].split(',"map_id_prefix"')[0]
            loclist = json.loads(temp)
            for loc in loclist:
                store_number = loc["entry_id"]
                latitude = loc["lat"]
                longitude = loc["long"]
                html = BeautifulSoup(loc["content"], "html.parser")
                location_name = html.find("h4").text
                log.info(location_name)
                raw_address = (
                    html.find("p")
                    .text.replace("Address:", "")
                    .replace("  County:", "")
                    .strip()
                )
                if "Costcutter Lifford" in location_name:
                    phone = "074 9141677"
                else:
                    phone = MISSING
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = "Ireland"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
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
