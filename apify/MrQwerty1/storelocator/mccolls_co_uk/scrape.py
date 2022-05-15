import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.mccolls.co.uk/storelocator/ajax/location/"
    r = session.get(api, headers=headers)
    js = json.loads(r.json())["items"]

    for j in js:
        location_name = j.get("name")
        page_url = j.get("store_url")
        street_address = f'{j.get("address")} {j.get("address_2") or ""}'.replace(
            "&amp;", "&"
        ).strip()
        city = j.get("town")
        state = j.get("state")
        postal = j.get("zip")
        country = j.get("country")

        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = j.get("trading_name")
        store_number = j.get("branch_id")

        _tmp = []
        text = j.get("schedule") or ""
        if text:
            hours_json = json.loads(f"[{text}]")
        else:
            hours_json = []

        for h in hours_json:
            for day, v in h.items():
                start = v.get("from") or []
                end = v.get("to") or []
                line = f'{day}: {":".join(start)}-{":".join(end)}'
                if "Closed" in line:
                    line = f"{day}: Closed"
                if "Event" in line:
                    continue
                _tmp.append(line)

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mccolls.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.mccolls.co.uk/storelocator/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
