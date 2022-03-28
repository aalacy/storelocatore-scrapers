from bs4 import BeautifulSoup
import json
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
    url = "https://www.thistle.com/thistle-express"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("div", {"class": "map-wrap"})
    for link in linklist:
        link = link.find("div")
        lat = link["data-latitude"]
        longt = link["data-longitude"]
        title = link["data-desc"].split(">", 1)[1].split("<", 1)[0]
        link = "https://www.thistle.com/thistle-express/" + link["data-slug"]
        r = session.get(link, headers=headers)
        content = r.text.split('<script type="application/ld+json">')[2].split(
            "</script", 1
        )[0]
        content = json.loads(content)
        street = content["address"]["streetAddress"]
        pcode = content["address"]["postalCode"]
        title = content["name"]
        phone = content["telephone"]
        state = content["address"]["addressRegion"]
        city = street.split(", ")[-1]
        street = street.split(", " + city, 1)[0]
        city = city.replace(pcode, "").strip()
        yield SgRecord(
            locator_domain="https://www.thistle.com/thistle-express",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state,
            zip_postal=pcode.strip(),
            country_code="GB",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
