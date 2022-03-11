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
    url = "https://www.pilgrimfurniturecity.com/stores/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "store-result"})

    for loc in loclist:
        store = loc["data-store-id"]
        lat = loc["data-lat"]
        longt = loc["data-lon"]
        link = loc.find("a", {"class": "store-result__name"})
        title = link.text
        link = link["href"]
        street = loc.find("div", {"class": "store-result__address__street1"}).text
        city = loc.find("span", {"class": "store-result__address__city"}).text
        state = loc.find("span", {"class": "store-result__address__state"}).text
        pcode = loc.find("span", {"class": "store-result__address__zip"}).text
        phone = loc.find("a", {"class": "store-result__phone"}).text
        hours = loc.find("div", {"class": "store-result__hours__hours"})
        hours = re.sub(cleanr, " ", str(hours)).strip().replace("Store Hours: ", "")

        yield SgRecord(
            locator_domain="https://www.pilgrimfurniturecity.com",
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
