from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mini-mart_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://mini-mart.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://mini-mart.com/locations"
        r = session.get(url, headers=headers)
        state_list = r.text.split("<h4")[1:]
        for state_url in state_list:
            state_url = "<h4" + state_url
            soup = BeautifulSoup(state_url, "html.parser")
            city = soup.find("h4").text
            loclist = soup.findAll("p")
            for loc in loclist:
                loc = loc.get_text(separator="|", strip=True).split("|")
                location_name = loc[0]
                log.info(location_name)
                try:
                    street_address = loc[1]
                except:
                    continue
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=MISSING,
                    zip_postal=MISSING,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=MISSING,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=MISSING,
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
