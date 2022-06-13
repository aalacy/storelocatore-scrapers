from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://www.mrclutch.com/branches"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("select", {"name": "branch_id"}).findAll("option")[1:]
    for link in linklist:
        title = link.text
        store = link["value"]
        link = link["data-url"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        address = soup.find("div", {"class": "location"}).find("p").text.strip()
        address = re.sub(pattern, "\n", address)
        pcode = address.splitlines()[-1]
        city = address.splitlines()[-2]
        street = address.split(city, 1)[0].replace("\n", " ").strip()
        phone = soup.find("div", {"class": "telephone"}).find("strong").text
        hours = (
            soup.find("div", {"class": "times"})
            .find("p")
            .text.replace("\n", " ")
            .strip()
        )
        try:
            hours = hours.split("Bank", 1)[0]
        except:
            pass
        lat, longt = (
            r.text.split("new google.maps.LatLng(", 1)[1]
            .split(")", 1)[0]
            .split(", ", 1)
        )

        yield SgRecord(
            locator_domain="https://www.mrclutch.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.strip(),
            country_code="GB",
            store_number=str(store),
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
