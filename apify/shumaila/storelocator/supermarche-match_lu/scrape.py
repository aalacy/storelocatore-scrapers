from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MISSING = SgRecord.MISSING


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.supermarche-match.lu/storelocator"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("li", {"class": "storeLocator-store"})
    for div in divlist:
        title = div.find("h2").text
        store = div["onclick"].split("openInfoWindow('", 1)[1].split("'", 1)[0]
        address = str(div.find("p", {"class": "storeLocator-store-address"}))
        address = re.sub(cleanr, " ", address).replace("\n", " ").strip()
        link = div.find("p", {"class": "storeLocator-store-moreLink"}).find("a")["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        lat, longt = (
            r.text.split('a href="https://www.google.com/maps/search/?api=1&query=', 1)[
                1
            ]
            .split('"', 1)[0]
            .split(",", 1)
        )
        phone = soup.find("a", {"class": "link--phone"}).text
        hourlist = div.find("table", {"class": "store-timetable-table"}).findAll("tr")
        hours = ""
        for hr in hourlist:
            hr = hr.findAll("td")
            hours = hours + hr[0] + " " + hr[2] + " "
        ltype = "Match"
        if "Smatch" in title:
            ltype = "Smatch"
        pa = parse_address_intl(address)

        street_address = pa.street_address_1
        street = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        pcode = zip_postal.strip() if zip_postal else MISSING

        yield SgRecord(
            locator_domain="https://www.supermarche-match.lu/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="LU",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
            raw_address=address,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
