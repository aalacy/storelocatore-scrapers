import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    base_url = "https://laparrilla.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    hours = (
        " ".join(list(soup.find_all("em")[-1].stripped_strings))
        .replace("OPENING TIME", "")
        .strip()
    )

    for script in soup.find_all("script"):
        if "var LPAD_SL = " in script.text:
            location_list = json.loads(
                script.text.split("var LPAD_SL = ")[1].split("};")[0] + "}"
            )["locations"]
            for store_data in location_list:
                store = []
                store.append("https://laparrilla.com")
                store.append(store_data["name"])
                store.append(store_data["_street_1"] + " " + store_data["_street_2"])
                store.append(store_data["_city"])
                store.append(store_data["_state"])
                store.append(store_data["_postal_code"])
                store.append("US")
                store.append("<MISSING>")
                phone = store_data["_phone"].replace("\u2013", "").strip()
                if not phone and "963-6110" in soup.text:
                    phone = "(404) 963-6110"
                store.append(phone)
                store.append("")
                store.append(store_data["_latitude"])
                store.append(store_data["_longitude"])
                store.append(hours)
                store.append(base_url)

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
