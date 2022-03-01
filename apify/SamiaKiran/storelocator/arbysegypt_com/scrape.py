from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "arbysegypt_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://arbysegypt.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.arbysegypt.com/branches"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "panel-body"})[2].findAll("li")
        for loc in loclist:
            raw_address = loc.text.replace("<!--: -->", "")
            loc = raw_address.split(":")
            city = loc[0]
            log.info(city)
            street_address = loc[1]
            phone = soup.select_one("a[href*=tel]")["href"].replace("tel:", "")
            country_code = "Egypt"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=MISSING,
                street_address=street_address.strip(),
                city=city.strip(),
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
