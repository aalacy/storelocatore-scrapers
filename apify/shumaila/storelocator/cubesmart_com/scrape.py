from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup

session = SgRequests()
headersss = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")

    url = "https://www.cubesmart.com/sitemap-facility.xml"
    r = session.get(url, headers=headersss)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("loc")
    for loc in loclist:

        link = loc.text
        r = session.get(link, headers=headersss)
        try:
            soup = BeautifulSoup(r.text, "html.parser")
        except:
            session1 = SgRequests()
            r = session1.get(link, headers=headersss)
            soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text
        try:
            address = soup.find("div", {"class": "csFacilityAddress"}).find("div").text
        except:

            continue
        street, city, state, pcode = address.split(", ")
        lat = r.text.split('"Latitude": ', 1)[1].split(",", 1)[0]
        longt = r.text.split('"Longitude": ', 1)[1].split("}", 1)[0].strip()
        store = link.split("/")[-1].split(".", 1)[0]

        phone = r.text.split('},"telephone":"', 1)[1].split('"', 1)[0]
        phone = phone.replace(")", ") ")
        try:
            hours = (
                r.text.split('<p class="csHoursList">', 1)[1]
                .split("</p>", 1)[0]
                .replace("&ndash;", " - ")
                .replace("<br>", " ")
                .lstrip()
            )
            hours = re.sub(cleanr, " ", hours).strip()
        except:

            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.cubesmart.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=str(city),
            state=str(state),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=store,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace("<br/>", " ").strip(),
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
