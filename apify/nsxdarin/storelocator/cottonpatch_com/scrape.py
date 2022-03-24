from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://cottonpatch.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("div", {"class": "location"})

    for div in linklist:

        title = div.find("h4").text
        address = div.findAll("p")[-2].text
        hours = (
            div.findAll("p")[-1].text.replace("\n", " ").replace("Hours:", "").strip()
        )
        address = re.sub(pattern, "\n", address).strip().splitlines()
        street = address[0]
        city, state = address[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = address[2]
        link = div.find("a")["href"]

        r = session.get(link, headers=headers)
        lat, longt = r.text.split("[{lat:", 1)[1].split("}", 1)[0].split(",", 1)
        longt = longt.replace("lng:", "")

        yield SgRecord(
            locator_domain="https://cottonpatch.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
