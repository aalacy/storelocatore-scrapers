from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.action.com/"
    api_url = "https://www.action.com/api/stores/coordinates/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]["items"]
    for j in js:

        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        r = session.get(f"https://www.action.com/api/stores/{store_number}/")
        js = r.json()["data"]
        slug = js.get("url")
        page_url = f"https://www.action.com{slug}"
        location_name = js.get("store")
        street_address = f"{js.get('houseNumber')} {js.get('street')}".replace(
            "None", ""
        ).strip()
        postal = js.get("postalCode")
        country_code = js.get("countryCode")
        city = js.get("city")
        hours = js.get("openingHours")
        tmp = []
        hours_of_operation = "<MISSING>"
        if hours:
            for h in hours:
                closed = h.get("closed")
                day = h.get("dayName")
                if not closed:
                    opens = h.get("thisWeek").get("opening")
                    closes = h.get("thisWeek").get("closing")
                    line = f"{day} {opens} - {closes}".replace(
                        "None - None", "Closed"
                    ).strip()
                    tmp.append(line)
                if closed:
                    line = f"{day} Closed"
                    tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
