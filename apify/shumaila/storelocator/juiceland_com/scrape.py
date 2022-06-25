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
    url = "https://www.juiceland.com/all-locations/"
    pattern = re.compile(r"\s\s+")
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "location-list-block__content"})
    for loc in loclist:
        title = loc.find("h4").text

        link = loc.find("a")["href"]

        try:
            street = loc.find("span", {"class": "address"}).text.replace(",", "")
        except:
            street = "<MISSING>"
        city = loc.find("span", {"class": "city"}).text.replace(",", "")
        state = loc.find("span", {"class": "state"}).text.replace(",", "")
        pcode = loc.find("span", {"class": "zip"}).text.replace(",", "")
        try:
            phone = loc.find("span", {"class": "phone"}).text.replace(",", "")
        except:

            phone = "<MISSING>"
        try:
            hours = loc.find("div", {"class": "single-wpsl__right-hours"}).text.strip()
            hours = re.sub(pattern, " ", hours).replace("Store Hours: ", "").strip()
        except:
            hours = "<MISSING>"
        r = session.get(link, headers=headers)
        try:
            lat = r.text.split('"lat":"', 1)[1].split('"', 1)[0]
            longt = r.text.split('"lng":"', 1)[1].split('"', 1)[0]
        except:
            lat = longt = "<MISSING>"
        if "Temp Closed" in title:

            hours = "Temp Closed"
        yield SgRecord(
            locator_domain="https://www.juiceland.com",
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
            hours_of_operation=hours.replace("\n", " ").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
