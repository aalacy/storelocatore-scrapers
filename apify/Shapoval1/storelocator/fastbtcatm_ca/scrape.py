import json
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://cdn.storelocatorwidgets.com/json/LDmfSFzNHUZleTxMVKMoEQkUAlunxgS9?callback=slw&_=1635247699705"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://fastbtcatm.ca/",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    jsblock = r.text.split("slw(")[1].split("})")[0].strip() + "}"
    js = json.loads(jsblock)
    for j in js["stores"]:

        page_url = "https://fastbtcatm.ca/"
        k = j.get("data")
        ad = "".join(k.get("address"))
        a = parse_address(International_Parser(), ad)
        location_name = j.get("name") or "<MISSING>"
        location_type = "ATM"
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        latitude = k.get("map_lat") or "<MISSING>"
        longitude = k.get("map_lng") or "<MISSING>"
        hours_of_operation = (
            "".join(k.get("description")).replace("\n", " ").strip() or "<MISSING>"
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
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://fastbtcatm.ca/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
