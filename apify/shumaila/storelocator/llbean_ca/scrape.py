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
    url = "https://www.llbean.ca/Retail.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.findAll("div", {"class": "row_intl"})[1].findAll("a")
    for alink in link_list:
        link = alink["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "color-medium-grey"})
        title = divlist[0].text
        title = re.sub(pattern, "", title).strip()
        address = divlist[1].text
        address = re.sub(pattern, "\n", address).strip().splitlines()
        street = address[0]
        city, state = address[1].split(", ", 1)
        state, pcode = state.strip().split(" ", 1)
        phone = divlist[2].text
        phone = re.sub(pattern, "", phone).strip()
        hours = divlist[6].text
        hours = re.sub(pattern, "\n", hours).replace("\n", " ").strip()
        ccode = "CA"
        lat, longt = (
            divlist[5]
            .find("a")["href"]
            .split("@", 1)[1]
            .split("data", 1)[0]
            .split(",", 1)
        )
        longt = longt.split(",", 1)[0]
        yield SgRecord(
            locator_domain="https://www.llbean.ca/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=lat,
            longitude=longt,
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
