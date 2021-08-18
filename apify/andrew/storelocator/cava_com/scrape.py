import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

BASE_URL = "https://cava.com/locations"


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(BASE_URL, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "cava.com"
    stores = base.find_all(class_="vcard")
    for store in stores:
        if "COMING SOON" in store.text.upper():
            continue
        location_name = store.h3.text
        street_address = store.find(class_="street-address").text.strip()
        city = store.find(class_="locality").text.replace(",", "")
        state = store.find(class_="region").text
        zipcode = store.find(class_="postal-code").text
        if "hours" in store.find_all(class_="copy")[-1].text.lower():
            hours_of_operation = (
                store.find_all(class_="copy")[-1].text.replace("Hours:", "").strip()
            )
        else:
            hours_of_operation = "<MISSING>"
        if "tel" in str(store.a):
            phone = store.a.text
        else:
            phone = "<MISSING>"

        store_number = "<MISSING>"
        try:
            store_number = store.find("a", string="Order Online")["href"]
            store_number = re.findall(r"stores\/{1}(\d*)", store_number)[0]
        except:
            pass

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=BASE_URL,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
