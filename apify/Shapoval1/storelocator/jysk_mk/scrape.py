from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.mk/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Access-Control-Expose-Headers": "*",
        "Authorization": "Bearer null",
        "loc": "",
        "dto": '{"kind":"server"}',
        "desired_lang": "mk",
        "Origin": "https://jysk.mk",
        "Connection": "keep-alive",
        "Referer": "https://jysk.mk/public/home?returnUrl=%2Fprivate",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    data = '{"return_excel_translations":false,"filters_join_operator_kind":1,"filters":[],"select_fields":[{"name":"org_unit_id","alias":"org_unit_id"},{"name":"name","alias":"name"},{"name":"description","alias":"description"},{"name":"primary_address","alias":"primary_address"},{"name":"primary_phone","alias":"primary_phone"},{"name":"primary_email","alias":"primary_email"}],"order_fields":[{"name":"ordering_no","mode":1}],"aggregate_fields":[],"skip":-1,"take":-1,"return_tree":false,"return_excel":false,"where":null,"tree_max_depth":null}'
    r = session.post(
        "https://jysk.mk/public/clickkon/whf/list", headers=headers, data=data
    )
    js = r.json()
    for j in js:
        a = j.get("addresses")[0]
        page_url = "https://jysk.mk/public/store"
        location_name = j.get("name")
        street_address = f"{a.get('line_1')} {a.get('line_2')}".strip()
        state = a.get("state_name") or "<MISSING>"
        postal = a.get("zip_code")
        country_code = "North Macedonia"
        city = a.get("city_name")
        latitude = a.get("coordinate_lat")
        longitude = a.get("coordinate_lng")
        phone = j.get("primary_phone")
        hours_of_operation = j.get("description")

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
            raw_address=j.get("primary_address"),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
