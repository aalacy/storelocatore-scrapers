from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.apcjp.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.apcjp.com/",
        "X-MICROCMS-API-KEY": "e5369660-10dd-4e6c-9efe-80c9fbd2739b",
        "Origin": "https://www.apcjp.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "If-None-Match": 'W/"8312-a1XJYi1xvj4UyFXwOlY4E2dd/D0"',
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    params = (("limit", "100"),)

    r = session.get(
        "https://store.microcms.io/api/v1/store-prd", headers=headers, params=params
    )
    js = r.json()["contents"]

    for j in js:

        page_url = "https://www.apcjp.com/jpn/shop_list/"
        location_name = j.get("store_name")
        ad = j.get("store_address")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if postal == "ELM1F":
            postal = "<MISSING>"
        country_code = "JP"
        city = a.city or "<MISSING>"
        map_link = j.get("store_link")
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = str(j.get("store_tel")) or "<MISSING>"
        if phone.find("(") != -1:
            phone = phone.split("(")[0].strip()
        hours_of_operation = j.get("store_hours") or "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
