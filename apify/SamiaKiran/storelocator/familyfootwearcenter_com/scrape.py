from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "familyfootwearcenter_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data(sgw: SgWriter):
    if True:
        url = "https://www.familyfootwearcenter.com/store-locations/shoe-stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "column3"}).findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "page-heading"}).text
            temp = soup.find("div", {"class": "page-content page-content--centered"})
            address = temp.get_text(separator="|", strip=True).split("|")
            phone = address[5]
            if "We encourage our customers" in address[7]:
                hours_of_operation = address[8] + " " + address[9]
            else:
                hours_of_operation = address[7] + " " + address[8]
            street_address = address[1]
            address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            sgw.write_row(
                SgRecord(
                    locator_domain="https://www.familyfootwearcenter.com/",
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude="<MISSING>",
                    longitude="<MISSING>",
                    hours_of_operation=hours_of_operation.strip(),
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
