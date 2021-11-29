import json

from bs4 import BeautifulSoup as bs

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://www.townfairtire.com"

    soup = bs(session.get("https://www.townfairtire.com/store/tires/").text, "lxml")

    for atag in soup.find("div", {"class": "storeLocations"}).find_all("a"):

        if "Stores:" in atag.text:
            continue

        page_url = base_url + atag["href"]

        soup1 = bs(session.get(base_url + atag["href"]).text, "lxml")
        latitude = json.loads(
            soup1.find("script", {"type": "application/ld+json"}).contents[0]
        )["geo"]["latitude"]
        longitude = json.loads(
            soup1.find("script", {"type": "application/ld+json"}).contents[0]
        )["geo"]["longitude"]

        if "-" not in str(longitude):
            longitude = float("-" + str(longitude))

        main1 = list(soup1.find("div", {"class": "storeInfo"}).stripped_strings)
        address = main1[0].strip()
        ct = main1[1].strip().split(",")
        city = ct[0].strip()
        state = ct[1].strip().split(" ")[0].strip()
        zipp = ct[1].strip().split(" ")[1].strip()
        phone = (
            soup1.find("div", {"id": "ContentPlaceHolder1_UpdatePanel2"})
            .find("button")
            .text.strip()
        )
        hour = " ".join(
            list(soup1.find("div", {"class": "storeHours"}).stripped_strings)[1:]
        )

        name = soup1.find("div", {"class": "tireBrand"}).find("h1").text.strip()

        store = []
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("Call ", "") if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")

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
