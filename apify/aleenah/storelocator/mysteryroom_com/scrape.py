from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("mysteryroom_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    res = session.get("https://mysteryroom.com/location/")
    soup = BeautifulSoup(res.text, "html.parser")
    sa = soup.find("div", {"class": "block sectioned-content"}).find_all("a")
    for a in sa:

        url = "https://mysteryroom.com" + a.get("href").replace(
            "https://allinadventures.com", ""
        )
        logger.info(url)
        loc = soup.find("h1").text
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        phone = (
            soup.find("span", {"id": "phone-1"})
            .text.replace("Click here to call ", "")
            .strip()
        )
        addr = (
            soup.find("span", {"id": "location-1"})
            .text.replace("Click here to view location ", "")
            .strip()
            .split("\n")
        )
        if len(addr) == 1:
            street = "<MISSING>"
            addr = addr[0]
        else:
            street = addr[0]
            addr = addr[1]
        if "," in addr:
            addr = addr.split(",")
            city = addr[0]
            addr = addr[1]
        else:
            city = "<MISSING>"

        addr = addr.strip().split(" ")

        state = addr[0]
        zip = addr[1]
        lis = soup.find_all("div", {"class": "block wysiwyg prose"})[1].find_all("li")

        tim = ""
        for li in lis:
            if li.find("ul"):
                continue
            tim += li.text.strip() + ", "

        tim = tim.strip(", ")

        yield SgRecord(
            locator_domain="https://mysteryroom.com",
            page_url=url,
            location_name=loc,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<INACCESSIBLE>",
            longitude="<INACCESSIBLE>",
            hours_of_operation=tim,
        )


def scrape():
    write_output(fetch_data())


scrape()
