from bs4 import BeautifulSoup
import json
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

    url = "https://www.chargrillusa.com/location/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("div", {"class": "location-list"}).select("a[href*=locations]")
    for link in linklist:
        title = link.text
        link = link["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loc = r.text.split('"markersData":', 1)[1].split("};", 1)[0]
        loc = json.loads(loc)[0]
        lat = loc["lat"]
        longt = loc["lng"]
        address = loc["address"].split(", ")
        street = address[0]
        city = address[1]
        state, pcode = address[2].split(" ", 1)
        phone = soup.select_one("a[href*=tel]").text
        try:
            hours = (
                soup.text.split("Hours:", 1)[1]
                .split("Char-Grill", 1)[0]
                .replace("\n", " ")
                .strip()
            )
        except:
            hours = "<MISSING>"
        try:
            hours = (
                hours.split("Hours:", 1)[1]
                .split("RDU", 1)[0]
                .replace("\n", " ")
                .strip()
            )
        except:
            pass
        if "call" in hours:
            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.chargrillusa.com/",
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
            hours_of_operation=str(hours.encode(encoding="ascii", errors="replace"))
            .replace("?", "-")
            .replace("b'", "")
            .strip()
            .replace("'", ""),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
