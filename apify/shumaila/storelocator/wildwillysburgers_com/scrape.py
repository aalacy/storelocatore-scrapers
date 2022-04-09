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

    url = "https://www.wildwillysburgers.com/locations/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=locations]")
    linked = []
    for link in linklist:
        title = link.text
        link = link["href"]
        if len(link.split("locations/", 1)[1]) < 5 or (link in linked):
            continue
        linked.append(link)

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.findAll("iframe")[-1]["src"]

        address = (
            soup.text.split("We’re located at", 1)[1]
            .split("Get Directions", 1)[0]
            .strip()
        )
        street, city, state = address.split(", ")
        state, pcode = state.split(" ", 1)
        longt, lat = content.split("!2d", 1)[1].split("!2m", 1)[0].split("!3d", 1)

        yield SgRecord(
            locator_domain="https://www.wildwillysburgers.com/",
            page_url=link,
            location_name=str(title.encode(encoding="ascii", errors="replace"))
            .replace("b'", "")
            .strip()
            .replace("'", "")
            .replace("?", "'")
            .replace("'''", "'"),
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
