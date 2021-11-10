import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


session = SgRequests()
website = "shopamericanrental_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
}

DOMAIN = "https://www.shopamericanrental.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.shopamericanrental.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", string=re.compile("View Page"))
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "col-md"})[-1]
            phone = temp.find("h4").text
            temp = temp.findAll("p")
            location_name = soup.find("h2").text
            address = temp[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0].replace("NEW LOCATION:", "")
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = (
                temp[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .split("facebook")[0]
                .replace("OPEN NOW", "")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
