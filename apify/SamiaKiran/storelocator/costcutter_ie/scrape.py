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
            loclist = soup.find("div", {"class": "gv-map-entries"}).findAll(
                "div", {"class": "gv-map-view"}
            )
            for loc in loclist:
                loc = loc.get_text(separator="|", strip=True).replace("|", " ")
                if "Phone:" in loc:
                    phone = loc.split("Phone:")[1]
                else:
                    phone = MISSING
                loc = loc.split("Store Address:")
                location_name = loc[0].replace("Store Name:", "")
                log.info(location_name)
                address = loc[1].split(" Store County: ")
                city = address[-1]
                raw_address = address[0]
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

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
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=MISSING,
                    raw_address=address[0] + " " + address[1],
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
