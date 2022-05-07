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

    url = "https://www.mrclutch.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    pattern = re.compile(r"\s\s+")
    linklist = soup.findAll("loc")
    for link in linklist:

        link = link.text
        try:
            check = link.split("/branch", 1)[1].split("/")

            if len(check) == 2:
                pass
            else:
                continue
        except:
            continue
        try:
            r = session.get(link, headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        street = soup.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = soup.find("span", {"itemprop": "addressLocality"}).text.strip()
        try:
            city, state = city.split(",")
        except:
            state = "<MISSING>"
        pcode = soup.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = soup.find("span", {"itemprop": "telephone"}).text.strip()
        hours = soup.find("div", {"class": "times"}).find("p").text.split("Bank", 1)[0]
        hours = hours.replace("\n", " ").strip()
        title = r.text.split('title: "', 1)[1].split('"', 1)[0]
        lat, longt = (
            r.text.split(" google.maps.LatLng(", 1)[1].split(")", 1)[0].split(", ", 1)
        )
        street = soup.find("div", {"class": "location"}).text.replace(
            "OUR LOCATION", ""
        )
        street = re.sub(pattern, " ", street).strip()
        street = street.split(city.strip(), 1)[0]

        yield SgRecord(
            locator_domain="https://www.mrclutch.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="GB",
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
