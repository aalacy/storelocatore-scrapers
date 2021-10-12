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
    url = "http://premierecinemas.net/contact"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    phonelist = soup.findAll("div", {"class": "threecol"})
    linklist = (
        soup.find("nav", {"id": "primary_nav_wrap"}).find("ul").find("ul").findAll("li")
    )
    for link in linklist:
        title = link.text
        link = "http://premierecinemas.net" + link.find("a")["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        location = soup.findAll("div", {"class": "sidelocation"})[-1]
        longt, lat = (
            location.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d", 1)
        )
        location = location.findAll("p")[-1]
        location = re.sub(cleanr, "\n", str(location))
        location = re.sub(pattern, "\n", str(location)).strip().splitlines()
        title = location[0]
        street = location[1]
        city, state = location[2].split(", ", 1)
        pcode = hours = "<MISSING>"

        for ph in phonelist:
            if city in ph.text:
                title = ph.find("h3").text
                phone = (
                    ph.text.split("Phone: ", 1)[1]
                    .split("Box", 1)[0]
                    .replace("\n", "")
                    .strip()
                )
                break
        if "TBD" in phone:
            phone = "<MISSING>"
            title = title + " - Coming Soon"
        yield SgRecord(
            locator_domain="http://premierecinemas.net",
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
