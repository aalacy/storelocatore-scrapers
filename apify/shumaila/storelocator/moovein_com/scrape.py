from bs4 import BeautifulSoup
import json
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

    url = "https://www.moovein.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    pattern = re.compile(r"\s\s+")
    linklist = soup.findAll("loc")
    for link in linklist:

        link = link.text
        try:
            check = link.split("/storage", 1)[1].split("/")

            if len(check) == 4:
                pass
            else:
                continue
        except:
            continue
        try:
            r = session.get(link, headers=headers)

            loc = r.text.split('<script type="application/ld+json">')[2].split(
                "</script>", 1
            )[0]
        except:
            continue
        store = (
            r.text.split("var facility =", 1)[1].split("id: ", 1)[1].split(",", 1)[0]
        )
        loc = json.loads(loc.replace("\n", ""))
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        try:
            city = loc["address"]["addressLocality"]
        except:
            city = "<MISSING>"
        try:
            state = loc["address"]["addressRegion"]
        except:
            state = "<MISSING>"
        pcode = loc["address"]["postalCode"]
        phone = loc["telephone"]
        lat = (
            r.text.split("label: '1'", 1)[1].split("latitude: ", 1)[1].split(",", 1)[0]
        )
        longt = (
            r.text.split("label: '1'", 1)[1].split("longitude: ", 1)[1].split("}", 1)[0]
        )
        longt = re.sub(pattern, "", str(longt))
        soup = BeautifulSoup(r.text, "html.parser")
        hours = soup.find("div", {"class": "facility-hours-panel"}).find("table").text
        hours = (
            re.sub(pattern, "\n", hours)
            .replace("\n", " ")
            .replace("Day Time ", "")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://www.moovein.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
