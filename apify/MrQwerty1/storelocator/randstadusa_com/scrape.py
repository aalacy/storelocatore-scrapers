from typing import Optional
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_value(data: Optional[list] = None):
    if data:
        return data.pop()
    return ""


def clean_phone(text: str):
    black_list = [",", "e", "o", "x", "&"]
    for b in black_list:
        if b in text:
            return text.split(b)[0].strip()
    return text


def fetch_data(sgw: SgWriter):
    data = '{"callback":"@Callbacks/getOverviewResults","currentRoute":{"path":"/locations/:searchParams*","url":"/locations/gv-map/","isExact":true,"params":{"searchParams":"gv-map/"},"routeName":"locations"},"data":{"language":"en"}}'
    api = "https://www.randstadusa.com/api/branches/get-callback"
    r = session.post(api, headers=headers, data=data)
    js = r.json()["searchResults"]["hits"]["hits"]

    for j in js:
        j = j.get("_source") or {}
        location_name = get_value(j.get("title"))
        slug = get_value(j.get("url"))
        page_url = f"https://www.randstadusa.com{slug}"
        adr1 = get_value(j.get("address_line1"))
        adr2 = get_value(j.get("address_line2"))
        street_address = f"{adr1} {adr2}".strip()
        city = get_value(j.get("city"))
        state = get_value(j.get("state"))
        postal = get_value(j.get("postal_code"))
        country = "US"

        phone = clean_phone(get_value(j.get("field_phone")))
        latitude = get_value(j.get("lat"))
        longitude = get_value(j.get("lng"))
        store_number = get_value(j.get("field_office_id"))

        _tmp = []
        starts = j.get("starthours") or []
        ends = j.get("endhours") or []
        days = j.get("day") or []
        _days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        cnt = 0
        for day in _days:
            try:
                s = starts[cnt]
                e = ends[cnt]
                s = str(s).zfill(4)
                e = str(e).zfill(4)
                start = f"{s[:2]}:{s[2:]}"
                end = f"{e[:2]}:{e[2:]}"
                inter = f"{start}-{end}"
            except IndexError:
                inter = "Closed"
            _tmp.append(f"{day}: {inter}")
            cnt += 1

        hours_of_operation = ";".join(_tmp)
        if not days:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.randstadusa.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Content-Type": "application/json;charset=utf-8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
