from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup


def fetch_data(sgw: SgWriter):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    session = SgRequests()
    r = session.get("https://bxfitness.com", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    for location in soup.find_all("ul", {"class": "sub-menu"})[1].find_all("a"):
        location_request = session.get(location["href"], headers=headers)
        location_soup = BeautifulSoup(location_request.text, "html.parser")

        hours = " ".join(
            list(location_soup.find("div", {"class": "hours-data"}).stripped_strings)
        )
        address = list(
            location_soup.find("div", {"class": "club-address"}).stripped_strings
        )

        geo_location = location_soup.find("iframe")["src"]
        name = location_soup.find("h1").text

        store = []
        store.append("https://bxfitness.com")
        store.append(name)
        store.append(address[1])
        store.append(address[2].split(",")[0])
        store.append(address[2].split(",")[1].replace("\xa0", " ").split(" ")[-2])
        store.append(address[2].split(",")[1].replace("\xa0", " ").split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1])
        store.append("<MISSING>")
        try:
            lat = geo_location.split("!3d")[1].split("!")[0]
            lng = geo_location.split("!2d")[1].split("!")[0]
        except:
            lat = ""
            lng = ""
        store.append(lat)
        store.append(lng)
        store.append(hours.replace("Club Hours", "").strip())
        store.append(location["href"])

        sgw.write_row(
            SgRecord(
                locator_domain=store[0],
                location_name=store[1],
                street_address=store[2],
                city=store[3],
                state=store[4],
                zip_postal=store[5],
                country_code=store[6],
                store_number=store[7],
                phone=store[8],
                location_type=store[9],
                latitude=store[10],
                longitude=store[11],
                hours_of_operation=store[12],
                page_url=store[13],
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
