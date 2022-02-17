import json
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_link = "https://maps.locations.hancockwhitney.com/api/getAsyncLocations?template=search&radius=1000&level=search&search=36608"
    data = session.get(base_link, headers=headers).json()["maplist"]

    base = BeautifulSoup(data, "lxml")
    js = (
        "["
        + base.text.replace("\r\n", "")
        .replace("\\", "")
        .replace("    ", "")
        .replace(': "{', ": {")
        .replace('}",', "},")[:-1]
        + "]"
    )
    stores = json.loads(js)

    for store_data in stores:
        store = []
        store.append("https://www.hancockwhitney.com")
        store.append("Hancock Whitney " + store_data["location_name"])
        try:
            street_address = store_data["address_1"] + " " + store_data["address_2"]
        except:
            street_address = store_data["address_1"]
        store.append(store_data["city"])
        store.append(store_data["region"])
        store.append(store_data["post_code"])
        store.append(store_data["country"])
        store.append(store_data["lid"])
        store.append(store_data["local_phone"])
        store.append(store_data["Location Type_CS"])
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        try:
            raw_days = store_data["hours_sets:primary"]["days"]
        except:
            hours = "<MISSING>"

        if not hours:
            for day in raw_days:
                hour = raw_days[day]
                try:
                    if hour == "closed":
                        clean_hours = day + " " + hour.title()
                    else:
                        opens = hour[0]["open"]
                        closes = hour[0]["close"]
                        clean_hours = day + " " + opens + "-" + closes
                    hours = (hours + " " + clean_hours).strip()
                except:
                    try:
                        hours = (hours + " " + day + " " + hour).strip()
                    except:
                        hours = "SOME OFF"
        link = store_data["url"]

        sgw.write_row(
            SgRecord(
                locator_domain=store[0],
                page_url=link,
                location_name=store[1],
                street_address=street_address,
                city=store[2],
                state=store[3],
                zip_postal=store[4],
                country_code=store[5],
                store_number=store[6],
                phone=store[7],
                location_type=store[8],
                latitude=store[9],
                longitude=store[10],
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
