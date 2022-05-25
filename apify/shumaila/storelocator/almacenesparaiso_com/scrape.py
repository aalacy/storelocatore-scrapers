from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://almacenesparaiso.com/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("ul", {"class": "sale-point"}).findAll("a")
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "footer-info-text"}).text.strip()
        content = content.split(" - ")
        title = content[0]
        street = content[1]
        city, state = content[2].split(" (", 1)
        state = state.replace(")", "")
        ccode = "CO"
        phone = content[3].split("Contáctanos: ", 1)[1].replace("(+57) ", "")

        yield SgRecord(
            locator_domain="https://almacenesparaiso.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal="<MISSING>",
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation="<MISSING>",
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
