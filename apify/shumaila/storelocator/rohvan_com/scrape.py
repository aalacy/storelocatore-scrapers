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
    url = "https://rohvan.com/contact-us/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "item"})
    for div in divlist:
        title = div.find("h5").text.replace(":", "").strip()
        info = div.find("div", {"class": "item-info"}).text.strip()
        phone = info.split("House: ", 1)[1].split("\n", 1)[0]
        hours = info.split("Open Hours:", 1)[1].split("\n", 1)[1].replace("\n", " ")
        address = info.splitlines()
        street, city = address[0].split(",", 1)
        city = city.replace(",", "").strip()
        state, pcode = address[1].split(" ", 1)
        lat, longt = (
            div.find("a", {"class": "holler-link"})["href"]
            .split("@", 1)[1]
            .split("data", 1)[0]
            .split(",", 1)
        )
        longt = longt.split(",", 1)[0]

        yield SgRecord(
            locator_domain="https://rohvan.com/",
            page_url=url,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
