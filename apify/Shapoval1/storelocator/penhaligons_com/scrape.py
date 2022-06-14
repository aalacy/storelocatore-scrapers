from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.penhaligons.com/us/en"
    api_url = "https://www.penhaligons.com/us/en/penhaligonsstorelocator/ajax/stores"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }

    data = {
        "latitude": "40.730610",
        "longitude": "-73.935242",
        "radius": "40075000",
        "filter": "",
        "type": "",
    }
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js["stores"]:

        a = j.get("address")
        street_address = f"{a.get('line1')} {a.get('line2')}".strip()
        if street_address.find("25 Kings Road") != -1:
            street_address = street_address.split(",")[0].strip()
        city = a.get("town")
        postal = a.get("postalCode")
        state = "<MISSING>"
        country_code = "".join(a.get("country").get("isocode"))
        slug1 = "".join(j.get("code"))
        slug2 = (
            "".join(j.get("displayName")).replace("'", "-").replace(" ", "-").lower()
        )
        page_url = f"https://www.penhaligons.com/us/en/stores/{slug2}/{slug1}"
        """if page_url.find("burlington-arcade") != -1:
            continue"""
        if page_url.find("canary-wharf") != -1:
            street_address = street_address + " " + "Canary Wharf"
        location_name = j.get("displayName")
        phone = a.get("phone") or "<MISSING>"
        latitude = j.get("geoPoint").get("latitude")
        longitude = j.get("geoPoint").get("longitude")
        location_type = j.get("puigStoreType")
        if location_type:
            location_type = "".join(location_type).strip()
        if location_type != "Store":
            continue
        status = j.get("status")
        hours = j.get("openingHours").get("weekDayOpeningList")[1:]
        tmp = []
        for h in hours:
            day = "".join(h["weekDay"])
            closed = "Closed"
            try:
                opens = "".join(h.get("openingTime").get("formattedHour"))
                close = "".join(h.get("closingTime").get("formattedHour"))
                line = f"{day} : {opens} - {close}"
                tmp.append(line)
            except AttributeError:
                line = f"{day} : {closed}"
                tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if status == "TEMPORARILY_CLOSED":
            hours_of_operation = "TEMPORARILY CLOSED".lower()
        store_number = a.get("id")

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
