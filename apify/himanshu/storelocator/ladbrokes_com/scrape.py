from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    addressesess = []
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }
    r_list = [
        "https://viewer.blipstar.com/searchdbnew?uid=2470030&lat=54.630057&lng=-3.550830&type=nearest&value=100000&keyword=&max=10000&sp=CA14%203QB&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.1969129058158794",
        "https://viewer.blipstar.com/searchdbnew?uid=2470030&lat=51.5284541234394&lng=-0.154586637827429&type=nearest&value=100000&keyword=&max=100000&sp=NW1&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.1874606795247602",
    ]
    for r_loc in r_list:

        r = session.get(r_loc, headers=headers).json()

        for index, anchor in enumerate(r):
            if index >= 1:

                adr = BeautifulSoup(anchor["a"], "lxml")
                city = (
                    adr.find("span", class_="storecity")
                    .text.replace("D.15", "Dublin")
                    .strip()
                )
                city = "".join(i for i in city if not i.isdigit())

                if city[-1:] == ".":
                    city = city[:-1]
                zipp = adr.find("span", class_="storepostalcode").text.strip()
                state = anchor["c"]
                country_code = "UK"
                if state == "ROI":
                    country_code = "IE"
                street_address = adr.text.strip().replace(city, "").replace(zipp, "")
                if street_address.count(city.title()) > 0:
                    index = street_address.rfind(city.title())
                    street_address = street_address[:index].strip()
                if len(street_address) < 10:
                    street_address = (
                        adr.text.strip().replace(city, "").replace(zipp, "")
                    )
                location_name = anchor["n"]
                store_number = location_name.split()[-1].strip()
                page_url = "https://help.ladbrokes.com/en/retail/shoplocator"
                phone = anchor["p"]
                hours = (
                    "mon "
                    + anchor["mon"]
                    + " tue "
                    + anchor["tue"]
                    + " wed "
                    + anchor["wed"]
                    + " thu "
                    + anchor["thu"]
                    + " fri "
                    + anchor["fri"]
                    + " sat "
                    + anchor["sat"]
                    + " sun "
                    + anchor["sun"]
                )
                location_type = "<MISSING>"
                latitude = anchor["lat"]
                longitude = anchor["lng"]
                store = []
                store.append("http://ladbrokes.com")
                store.append(location_name)
                store.append(
                    street_address.replace("Shoping Centre", "").replace(
                        "Shopping Centre", ""
                    )
                )
                store.append(city.strip())
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                store = [x.replace("–", "-") if type(x) == str else x for x in store]
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2] in addressesess:
                    continue
                addressesess.append(store[2])

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
