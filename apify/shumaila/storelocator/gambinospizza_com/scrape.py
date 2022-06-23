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
    url = "https://gambinospizza.com/locations-sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "xml")
    divlist = soup.findAll("loc")[1:]

    for div in divlist:
        link = div.text
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.replace("Gambino's Pizza in ", "")
        content = (
            re.sub(pattern, "\n", soup.text)
            .strip()
            .split(soup.find("h1").text + "\n", 1)[1]
            .split(title + " Coupons & Offers", 1)[0]
        )
        street = content.splitlines()[0]
        city = content.splitlines()[1].replace(",", "").strip()
        state = content.splitlines()[2]
        pcode = content.splitlines()[3]
        phone = content.splitlines()[6]
        hours = content.split(" Page", 1)[1]

        coordlink = soup.find("iframe")["src"]
        r = session.get(coordlink, headers=headers)
        try:
            lat, longt = (
                r.text.split(', USA",null,[null,null,', 1)[1]
                .split("]", 1)[0]
                .split(",", 1)
            )
        except:

            lat, longt = (
                r.text.split(" " + str(pcode) + '",null,[null,null,', 1)[1]
                .split("]", 1)[0]
                .split(",", 1)
            )
        yield SgRecord(
            locator_domain="https://gambinospizza.com/",
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
            hours_of_operation=hours.replace("•", " ").replace("\n", " ").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
