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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://marmaladecafe.com/locations"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "uk-panel-box"})
    for div in divlist:
        title = div.find("h3").text.strip()
        link = "https://marmaladecafe.com" + div.find("h3").find("a")["href"]
        print(title)
        div = re.sub(cleanr, "\n", str(div))
        div = re.sub(pattern, "\n", str(div)).strip()
        address = (
            div.split("Address", 1)[1].split("\n", 1)[1].split("TEL", 1)[0].splitlines()
        )
        street = address[0]
        city, state = address[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = div.split("TEL : ", 1)[1].split("\n", 1)[0]
        hours = (
            div.split("Hours", 1)[1]
            .split("\n", 1)[1]
            .split("Order", 1)[0]
            .replace("\n", " ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://marmaladecafe.com/",
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
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation=hours.replace("&amp;", "-").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
