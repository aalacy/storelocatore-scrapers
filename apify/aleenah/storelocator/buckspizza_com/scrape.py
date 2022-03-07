from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "buckspizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://buckspizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://buckspizza.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div",
            {"class": "nd_options_display_table_cell nd_options_vertical_align_bottom"},
        )[:-2]
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if "franchise-information" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                location_name = soup.find("h1").text
            except:
                continue
            temp = soup.findAll("div", {"class": "wpb_wrapper"})[1].findAll("h3")
            try:
                address = temp[0].get_text(separator="|", strip=True).split("|")
            except:
                address = (
                    soup.findAll("p")[1].get_text(separator="|", strip=True).split("|")
                )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            try:
                phone = temp[1].text
            except:
                phone = (
                    soup.findAll("div", {"class": "wpb_wrapper"})[1]
                    .findAll("h2")[1]
                    .text
                )
            hours_of_operation = (
                soup.findAll("p")[2]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if "DINE-IN" in hours_of_operation:
                hours_of_operation = MISSING
            country_code = "US"
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
