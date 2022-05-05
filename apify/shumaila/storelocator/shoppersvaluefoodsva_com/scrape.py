from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "http://www.shoppersvaluefoodsva.com/location/index.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "store-listing"})

    for loc in loclist:
        lat, longt = (
            loc.find("a")["href"].split("=", 1)[1].split("&", 1)[0].split("+", 1)
        )
        loc = re.sub(pattern, "\n", loc.text).strip().splitlines()

        street = loc[2]
        city, state = loc[3].split(", ", 1)
        state, pcode = state.split(" ", 1)
        hours = loc[4].replace("Hours: ", "").split(" DAILY", 1)[0]
        try:
            hours = hours.split("Direc", 1)[0]
        except:
            pass
        yield SgRecord(
            locator_domain="http://www.shoppersvaluefoodsva.com/",
            page_url=url,
            location_name="Shoppers Value Foods",
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=lat,
            longitude=longt,
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
