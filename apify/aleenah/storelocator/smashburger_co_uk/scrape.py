from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("smashburger_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():

    all = []

    res = session.get("https://smashburger.co.uk/locations")
    soup = BeautifulSoup(res.text, "html.parser")
    stores = soup.find_all(
        "div", {"class": "location d-flex flex-column pb-1 col-12 col-lg-6 col-xl-4"}
    )
    logger.info(len(stores))

    for store in stores:
        loc = store.find("div", {"class": "image-overlay"}).text.strip()

        days = store.find("ul").find_all("li")
        tim = ""
        for day in days:
            tim += day.text + ", "
        tim = tim.strip(", ")

        addr = store.find("p", {"class": "w-100"}).text.strip().split(loc)
        if len(addr) == 1:
            addr = addr[0].split(",")
            zip = addr[-1].strip()
            del addr[-1]
            street = ", ".join(addr)
        else:

            zip = addr[-1].split(",")[-1].strip()
            del addr[-1]
            street = ", ".join(addr)

        phone = str(store.find("i", {"class": "fa fa-phone"}).nextSibling)
        yield SgRecord(
            locator_domain="https://smashburger.co.uk",
            page_url="https://smashburger.co.uk/locations",
            location_name=loc,
            street_address=street.strip().strip(","),
            city=loc,
            state="<MISSING>",
            zip_postal=zip,
            country_code="GB",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<MISSING>",
            longitude="<MISSING>",
            hours_of_operation=tim.strip(),
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
