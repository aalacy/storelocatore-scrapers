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

    url = "http://malaniworldmercato.com/#location"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "location"})
    coordlist = soup.findAll("iframe")
    p = 0
    for loc in loclist:
        loc = re.sub(pattern, "\n", loc.text).strip()
        title = loc.split("\n", 1)[0]
        address = loc.split("\n", 1)[1].split(", USA", 1)[0].splitlines()
        city, state = address[-1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        street = " ".join(address[0 : len(address) - 1])
        phone = loc.split("Phone no: ", 1)[1].split("\n", 1)[0]
        hours = loc.split("Timings", 1)[1].split("\n", 1)[1].replace("\n", " ").strip()
        hours = hours.encode("ascii", "ignore").decode("ascii")
        longt, lat = (
            coordlist[p]["src"].split("!2d", 1)[1].split("!2m", 1)[0].split("!3d", 1)
        )
        p += 1

        yield SgRecord(
            locator_domain="http://malaniworldmercato.com",
            page_url=url,
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
