from bs4 import BeautifulSoup
import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "https://traviniaitaliankitchen.com/mobile/travinia-locations.php"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("div", {"class": "box-burg"})

    for link in linklist:

        link = link.find("a")["href"]
        if link == "#":
            continue
        if link.find("https:") == -1:
            link = "https://www.traviniaitaliankitchen.com/mobile/" + link
        r = session.get(link, headers=headers)
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            content = soup.find("h3").text
        except:
            continue
        content = re.sub(pattern, "\n", content).strip().splitlines()

        title = content[0]
        phone = content[-1]
        city, state = content[-2].split(", ", 1)
        street = " ".join(content[1 : len(content) - 2])
        state, pcode = state.split(" ", 1)

        hours = soup.text.split("HOURS", 1)[1].split("FIND", 1)[0]
        hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
        try:
            hours = hours.split("(Brunch", 1)[0]
        except:
            pass
        try:
            lat, longt = (
                r.text.split('"https://www.google.com/maps', 1)[1]
                .split("@", 1)[1]
                .split(",3a", 1)[0]
                .split(",")
            )
        except:
            try:
                lat, longt = (
                    r.text.split('"https://www.google.com/maps', 1)[1]
                    .split("@", 1)[1]
                    .split(",16z", 1)[0]
                    .split(",")
                )
            except:
                lat = longt = "<MISSING>"
        if len(street) < 3:
            street = title
            title = city
        yield SgRecord(
            locator_domain="https://www.traviniaitaliankitchen.com/",
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
