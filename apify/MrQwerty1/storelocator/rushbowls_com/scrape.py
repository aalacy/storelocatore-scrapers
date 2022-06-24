import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://rushbowls.com/locations"
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = text.split("var locations =")[1].split("}};")[0] + "}}"
    js = json.loads(text)

    for j in js.values():
        street_address = (
            f"{j.get('fran_address') or ''} {j.get('fran_address_2') or ''}".strip()
        )
        city = j.get("fran_city")
        state = j.get("fran_state") or SgRecord.MISSING
        if len(state) > 2 and state != SgRecord.MISSING:
            state = "TX"
        postal = j.get("fran_zip")
        if street_address == SgRecord.MISSING and postal == SgRecord.MISSING:
            continue
        country_code = "US"
        store_number = j.get("id")
        page_url = j.get("fran_web_address")
        location_name = j.get("fran_location_name")
        phone = j.get("fran_phone") or ""
        if "coming" in phone.lower():
            phone = SgRecord.MISSING
        latitude = j.get("fran_latitude")
        longitude = j.get("fran_longitude")

        _tmp = []
        source = j.get("gmb_hours") or "[]"
        hours = json.loads(source)
        for h in hours:
            day = h.get("openDay")
            s = h.get("openTime")
            e = h.get("closeTime")
            if isinstance(s, dict):
                start = (
                    str(s.get("hours")).zfill(2) + ":" + str(s.get("minutes")).zfill(2)
                )
                end = (
                    str(e.get("hours")).zfill(2) + ":" + str(e.get("minutes")).zfill(2)
                )
                inter = f"{start}-{end}"
            else:
                inter = f"{s}-{e}"

            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)
        status = j.get("status") or ""
        if "coming" in status:
            hours_of_operation = "Coming Soon!"

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://rushbowls.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
