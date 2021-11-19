from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://loomisexpress.com/"
    api_url = "https://loomisexpress.com/loomship/Common/queryLocations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://loomisexpress.com",
        "Connection": "keep-alive",
        "Referer": "https://loomisexpress.com/loomship/Shipping/DropOffLocations",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = '{"origin_lat":48.4824429,"origin_lng":-123.39337777551245,"include_otc":true,"include_smart":true,"include_terminal":true,"limit":5000,"within_distance":10000}'

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js:

        page_url = "https://loomisexpress.com/loomship/Shipping/DropOffLocations"
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('address_line_1')}"
        store_number = "".join(j.get("address_id")).strip() or "<MISSING>"
        city = "".join(j.get("city")).strip() or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CA"
        phone = "".join(j.get("phone")).strip() or "<MISSING>"
        if "MON-FRI: 08:30-1" in phone:
            phone = "<MISSING>"
        if phone == "<MISSING>":
            phone = "".join(j.get("address_line_2")).strip() or "<MISSING>"
        if phone.find("C/O WHITELAND FREIGHT") != -1:
            phone = "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        if phone == "UNIT 1 & 2":
            phone = "<MISSING>"
            street_address = street_address + " " + "UNIT 1 & 2"
        if phone == "unit 2":
            phone = "<MISSING>"
            street_address = street_address + " " + "unit 2"
        if phone == "UNIT 3":
            phone = "<MISSING>"
            street_address = street_address + " " + "UNIT 3"
        if phone == "Unit 22":
            phone = "<MISSING>"
            street_address = street_address + " " + "Unit 22"
        if phone == "UNIT 2":
            phone = "<MISSING>"
            street_address = street_address + " " + "UNIT 2"
        if phone == "Unit H4":
            phone = "<MISSING>"
            street_address = street_address + " " + "Unit H4"
        if phone == "UNIT 21":
            phone = "<MISSING>"
            street_address = street_address + " " + "UNIT 21"
        if phone == "UNIT 234":
            phone = "<MISSING>"
            street_address = street_address + " " + "UNIT 234"
        if (
            phone == "( BESIDE KENNER HIGH SCHOOL)"
            or phone == "AT REAR, ACCESS FROM MARCHET & VALET ST."
        ):
            phone = "<MISSING>"
        if phone.find("UNI") != -1:
            street_address = street_address + " " + " ".join(phone.split()[:-1])
            phone = phone.split()[-1].strip()
        street_address = street_address.replace(".", "").upper()
        latitude = j.get("latLng")[0] or "<MISSING>"
        longitude = j.get("latLng")[1] or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("attention"))
            .replace(". Loca", "")
            .replace("<b", "")
            .replace("<BR>", " ")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("By") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("BY APPOINTMENT") != -1:
            hours_of_operation = "<MISSING>"
        if store_number == "<MISSING>":
            continue

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
