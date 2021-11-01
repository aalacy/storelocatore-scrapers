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
    url = "https://www.harpsfood.com/StoreLocator/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=State]")
    for div in divlist:
        statelink = div["href"].replace("..", "https://www.harpsfood.com")
        r = session.get(statelink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", {"class": "StoreViewLink"})
        for link in linklist:
            link = link["href"]
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("h3").text.strip()
            try:
                store = title.split("#", 1)[1]
            except:
                store = link.split("L=", 1)[1].split("&", 1)[0]
            address = soup.find("p", {"class": "Address"}).text
            address = re.sub(pattern, "\n", address).strip().splitlines()
            street = address[1]
            city, state = address[2].split(", ", 1)
            state, pcode = state.split(" ", 1)
            phone = soup.find("p", {"class": "PhoneNumber"}).find("a").text.strip()
            try:
                hours = (
                    soup.find("table", {"id": "hours_info-BS"})
                    .text.split("Hours of Operation:", 1)[1]
                    .split("Holiday Hours:", 1)[0]
                    .strip()
                )
            except:
                hours = "<MISSING>"
            try:
                hours = hours.split("\n", 1)[0]
            except:
                pass
            maplink = (
                "https://www.harpsfood.com/StoreLocator/Store_MapDistance_S.las?miles=10&zipcode="
                + str(pcode)
            )
            try:
                r = session.get(maplink, headers=headers).json()[0]
                lat = r["Latitude"]
                longt = r["Longitude"]
            except:
                lat = longt = "<MISSING>"
            try:
                store = store.split(" ", 1)[0]
            except:
                pass
            yield SgRecord(
                locator_domain="https://www.harpsfood.com/",
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
    results = fetch_data()

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
