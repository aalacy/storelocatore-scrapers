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

    pattern = re.compile(r"\s\s+")
    url = "https://southmoonunder.com/pages/store-locator"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "store-locator"}).findAll(
        "div", {"class": "block"}
    )

    for div in divlist:
        content = re.sub(pattern, "\n", div.text).strip().splitlines()

        m = 0
        title = content[m]
        m = m + 1
        street = content[m]
        m = m + 1
        try:
            city, state = content[m].split(", ", 1)
        except:
            m = m + 1
            city, state = content[m].split(", ", 1)
        m = m + 1
        try:
            state, pcode = state.split(" ", 1)
        except:
            pcode = state[2:]
            state = state[0:2]
        phone = content[-1]
        hours = " ".join(content[m : len(content) - 2]).replace("|", "").strip()
        lat, longt = (
            div.find("a")["href"].split("@", 1)[1].split("data", 1)[0].split(",", 1)
        )
        longt = longt.split(",", 1)[0]

        yield SgRecord(
            locator_domain="https://southmoonunder.com/",
            page_url=SgRecord.MISSING,
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
