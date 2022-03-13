from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://local.gcrtires.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("div", {"id": "contains-place"}).findAll("a")
    for st in statelist:
        stlink = "https://local.gcrtires.com" + st["href"]
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.find("div", {"id": "contains-place"}).findAll("a")
        for div in divlist:
            divlink = "https://local.gcrtires.com" + div["href"]
            r = session.get(divlink, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"id": "location-list"})
            for loc in loclist:
                store = loc["data-currentlocation"]
                loc = loc.find("div", {"class": "place"})

                title = loc.find("strong").text
                link = "https://local.gcrtires.com" + loc.find("a")["href"]
                street = loc.find("div", {"class": "street"}).text
                city, state = loc.find("div", {"class": "locality"}).text.split(", ", 1)
                state, pcode = state.split(" ", 1)
                phone = loc.find("a", {"class": "list-location-phone-number"}).text
                r = session.get(link, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                hours = (
                    soup.find("div", {"class": "hours"})
                    .text.replace("Hours Today", "")
                    .strip()
                )
                lat, longt = (
                    loc.find("a", {"class": "list-location-cta-button"})["href"]
                    .split("/")[-1]
                    .split(",", 1)
                )
                hours = re.sub(pattern, " ", hours).strip().replace("Hours:", "")
                yield SgRecord(
                    locator_domain="https://www.gcrtires.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type="<MISSING>",
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
