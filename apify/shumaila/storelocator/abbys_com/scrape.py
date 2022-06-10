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

    url = "https://abbys.com/find-us/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location-overview"})
    for div in divlist:

        title = div.find("h3").text
        link = div.find("a")["href"]
        address = str(div.find("p")).split("<br/>", 1)
        street = address[0].replace("<p>", "").strip()
        city, state = address[1].replace("</p>", "").strip().split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = str(div).split('fa-phone-square"></i> ', 1)[1].split("</p", 1)[0]
        hours = (
            div.find("table", {"class": "location-hours"})
            .text.replace("\n", " ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://abbys.com/",
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
