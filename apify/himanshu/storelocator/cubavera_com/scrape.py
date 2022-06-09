import json

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
    base_url = "https://www.cubavera.com"
    r = session.get(
        "https://api.zenlocator.com/v1/apps/app_txdmatvw/locations/search?northeast=77.064637%2C149.5221&southwest=-57.442352%2C-180",
        headers=headers,
    )
    data = r.json()["locations"]
    return_main_object = []
    for store_data in data:
        if "coming soon" in store_data["address"].lower():
            continue
        store = []
        store.append("https://www.cubavera.com")
        store.append(store_data["name"])
        if store_data["address"] == "":
            store.append(store_data["address1"] + " " + store_data["address2"])
        else:
            store.append(
                " ".join(store_data["address"].split(",")[:-2]).replace("\n", " ")
            )
        store.append(store_data["city"])
        if store[-1] == "":
            store[-1] = store_data["visibleAddress"].split(",")[1]
        store.append(store_data["region"])
        store.append(
            store_data["postcode"] if store_data["postcode"] != "" else "<MISSING>"
        )
        if store[-1] == "<MISSING>":
            store[-1] = store_data["address"].split(" ")[-1]

        store.append(store_data["countryCode"])
        store.append(store_data["id"].replace("loc_", ""))
        store.append(
            store_data["contacts"]["con_ha9dqw4s"]["text"]
            if "con_ha9dqw4s" in store_data["contacts"]
            else "<MISSING>"
        )
        store.append("")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        if store_data["hours"] == "":
            store.append("<INACCESSIBLE>")
        else:
            try:
                store_hours = store_data["hours"]["hoursOfOperation"]
                for key in store_hours:
                    hours = hours + " " + key + " " + store_hours[key]
            except:
                pass
            store.append(hours if hours != "" else "<INACCESSIBLE>")

        sgw.write_row(
            SgRecord(
                locator_domain=store[0],
                page_url="https://www.cubavera.com/pages/store-locator",
                location_name=store[1],
                street_address=store[2].split("  ")[0].strip(),
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
