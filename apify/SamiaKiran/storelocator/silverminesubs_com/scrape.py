import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "silverminesubs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://silverminesubs.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.silverminesubs.com/locations/"
        r = session.get(url, headers=headers)
        state_list = r.text.split("<h2>")[2:]
        for temp_state in state_list:
            state = temp_state.split("</h2>")[0]
            loclist = temp_state.split('<div class="storerow">')[1:]
            for loc in loclist:
                loc = loc.split('<div class="break"></div>')[0]
                loc = BeautifulSoup(loc, "html.parser")
                loc = loc.get_text(separator="|", strip=True).split("|")
                location_name = strip_accents(loc[0])
                log.info(location_name)
                city = location_name.split()[0]
                street_address = loc[1]
                raw_address = street_address + " " + city + " " + state
                if "Fort" in city:
                    city = "Fort Collins"
                phone = loc[2]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city,
                    state=state,
                    zip_postal=MISSING,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
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
