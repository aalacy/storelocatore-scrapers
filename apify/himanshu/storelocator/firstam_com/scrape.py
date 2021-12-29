from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    r = session.get(
        "https://www.firstam.com/services-api/api/alta/search?take=100000&skip=0&officeDisplayFlag=true&officeZipCode=&officeStatus=active"
    )
    data = r.json()
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.firstam.com")
        store.append(store_data["officeName"])
        if not store_data["officeAddressLine1"]:
            continue
        store.append(
            store_data["officeAddressLine1"] + store_data["officeAddressLine2"]
            if store_data["officeAddressLine2"]
            else store_data["officeAddressLine1"]
        )
        store.append(store_data["officeCity"])
        store.append(store_data["officeState"])
        zip_code = (
            store_data["officeZipCode"]
            .replace(".", "")
            .replace("Cobb", "30064")
            .replace("74820 5801", "74820")
            .strip()
        )
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        if len(zip_code) < 4:
            zip_code = ""
        store.append(zip_code)
        store.append("US")
        store.append(store_data["officeId"])
        store.append(
            store_data["officePhoneAreaCode"] + " " + store_data["officePhoneNumber"]
            if store_data["officePhoneAreaCode"]
            else "<MISSING>"
        )
        store.append(
            store_data["companyName"] if store_data["companyName"] else store[1]
        )
        store.append(
            store_data["officeLatitude"]
            if store_data["officeLatitude"]
            else "<MISSING>"
        )
        store.append(
            store_data["officeLongitude"]
            if store_data["officeLongitude"]
            else "<MISSING>"
        )
        store.append("<MISSING>")
        link = "https://www.firstam.com/title/find-an-office/"

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
                page_url=link,
            )
        )


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
    )
) as writer:
    fetch_data(writer)
