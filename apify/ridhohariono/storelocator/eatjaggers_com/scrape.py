from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.eatjaggers.com/"
    api_url = "https://nomnom-prod-api.eatjaggers.com/restaurants/near?lat=40.751687&long=-74.004544&radius=200000&limit=600&nomnom=calendars&nomnom_calendars_from=20220615&nomnom_calendars_to=20220623&nomnom_exclude_extref=999"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["restaurants"]
    for j in js:

        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("storename") or "<MISSING>"
        street_address = j.get("streetaddress") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"
        hours = j.get("calendars").get("calendar")
        tmp = []
        for h in hours:
            typee = h.get("type")
            if typee != "business":
                continue
            ranges = h.get("ranges")
            for r in ranges[:7]:
                day = r.get("weekday")
                opens = r.get("start")
                opens = str(opens).split()[1].strip()
                closes = r.get("end")
                closes = str(closes).split()[1].strip()
                line = f"{day} {opens} - {closes}"
                tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        if (
            street_address == "1 World Trade Center"
            and hours_of_operation == "<MISSING>"
        ):
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
            store_number=SgRecord.MISSING,
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
