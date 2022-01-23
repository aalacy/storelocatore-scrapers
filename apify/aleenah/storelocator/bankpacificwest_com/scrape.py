from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification
logger = SgLogSetup().get_logger("pacificwestbank_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


def fetch_data():

    with SgChrome() as driver:
        driver.get("https://www.pacificwestbank.com/Get-In-Touch")
        soup = BeautifulSoup(driver.page_source, "html.parser")
    trs = soup.find("section", {"class": "subsection"}).find_all("tr")

    for tr in trs:

        tr = tr.find("td")

        name = tr.find("h3").text.strip()
        ps = tr.find_all("p")
        all = str(ps[0]).replace("<p>", "").replace("</p>", "").split("<br/>")
        street = all[0]
        phone = ps[2].text
        tim = ps[3].text.replace("Hours: ", "").replace("M-F,", "Monday - Friday: ")
        all = all[1].split(",")
        city = all[0]
        all = all[1].strip().split(" ")
        state = all[0]
        zip = all[1]

        yield SgRecord(
            locator_domain="https://www.pacificwestbank.com",
            page_url="https://www.pacificwestbank.com/Get-In-Touch",
            location_name=name,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<MISSING>",
            longitude="<MISSING>",
            hours_of_operation=tim.strip(),
        )


def scrape():
    write_output(fetch_data())


scrape()
