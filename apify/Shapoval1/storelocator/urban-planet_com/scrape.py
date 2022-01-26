from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        opens = h.get("open_time")
        closes = h.get("close_time")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://urban-planet.com/"
    api_url = "https://urban-planet.com/apps/api/v1/stores?location[latitude]=49.912234&location[longitude]=-97.20437740000001&location[radius]=10000&location[units]=km"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:
        a = j.get("address")
        page_url = f"https://urban-planet.com/pages/{j.get('store_handle')}"
        location_type = "".join(j.get("brand"))
        location_name = "".join(a.get("name")) + " " + location_type
        street_address = (
            f"{a.get('line1')} {a.get('line2')} {a.get('line3')}".replace(
                ",", ""
            ).strip()
            or "<MISSING>"
        )
        state = a.get("state_code") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = a.get("country_code") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("store_code") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("open_hours")
        hours_of_operation = get_hours(hours) or "<MISSING>"

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
