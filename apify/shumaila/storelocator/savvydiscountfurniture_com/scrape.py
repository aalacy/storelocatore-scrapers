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
    url = "https://www.savvydiscountfurniture.com/showroom-locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.select('a:contains("STORE INFO")')
    for loc in loclist:
        title = loc.text.strip()
        link = "https://www.savvydiscountfurniture.com" + loc["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = re.sub(cleanr, "\n", str(soup)).strip()
        content = re.sub(pattern, "\n", str(content)).strip()

        hours = (
            content.split("STORE HOURS", 1)[1]
            .split("ABOUT THIS STORE", 1)[0]
            .replace("\n", " ")
            .strip()
        )
        content = (
            content.split("Call:", 1)[1]
            .split("Get Directions to this Store", 1)[0]
            .strip()
            .splitlines()
        )
        street = content[1]
        city, state = content[2].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = content[0]
        lat, longt = soup.select_one("a[href*=dir]")["href"].split("/")[-1].split(",")
        coord = soup.select_one("a[href*=maps]")["href"]
        m = session.get(coord, headers=headers)
        try:
            lat, longt = m.url.split("@", 1)[1].split("data", 1)[0].split(",", 1)
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"

        yield SgRecord(
            locator_domain="https://www.savvydiscountfurniture.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone.strip(),
            location_type="<MISSING>",
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
