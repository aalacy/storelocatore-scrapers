from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.delarte.fr/"
    api_url = "https://www.delarte.fr/restaurants/getStores?q=&editing=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["result"]
    for j in js:

        a = j.get("address")
        slug = j.get("url")
        page_url = f"https://www.delarte.fr{slug}"
        location_name = j.get("displayName") or "<MISSING>"
        ad = a.get("line1") or "<MISSING>"
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "FR"
        city = a.get("town") or "<MISSING>"
        store_number = j.get("name") or "<MISSING>"
        latitude = j.get("geoPoint").get("latitude") or "<MISSING>"
        longitude = j.get("geoPoint").get("longitude") or "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("advancedOpeningDays")
        tmp = []
        if hours:
            for h in hours:
                day = (
                    str(h.get("dayOfWeek"))
                    .replace("1", "Monday")
                    .replace("2", "Tuesday")
                    .replace("3", "Wednesday")
                    .replace("4", "Thursday")
                    .replace("5", "Friday")
                    .replace("6", "Saturday")
                    .replace("7", "Sunday")
                )
                try:
                    opens = f"{h.get('openingClosingTimes')[0].get('openingHour')}:{h.get('openingClosingTimes')[0].get('openingMinute')}"
                    closes = f"{h.get('openingClosingTimes')[0].get('closingHour')}:{h.get('openingClosingTimes')[0].get('closingMinute')}"
                except:
                    opens = "Closed"
                    closes = "Closed"
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace("Closed - Closed", "Closed").strip()
            )

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
            raw_address=f"{ad} {city}, {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
