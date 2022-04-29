from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = (
        "https://in.sunglasshut.com/index.php?route=wk_store_locator/wk_store_locator"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://in.sunglasshut.com",
        "Connection": "keep-alive",
        "Referer": "https://in.sunglasshut.com/index.php?route=wk_store_locator/wk_store_locator",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    params = (("route", "extension/module/wk_store_locater/setter"),)

    data = {
        "longitude": "0",
        "latitude": "0",
        "city": "all",
        "location": "Name of Town or City",
    }

    r = session.post(
        "https://in.sunglasshut.com/index.php",
        headers=headers,
        params=params,
        data=data,
    )
    lines = r.text.split("~")[:-1]

    for line in lines:
        _tmp = line.split("!")
        store_number = _tmp.pop(0)
        latitude = _tmp.pop(0)
        longitude = _tmp.pop(0)
        location_name = _tmp.pop(0)
        raw_address = _tmp.pop(0)
        if ";" in raw_address:
            phone = (
                raw_address.split(";")[-1].replace(":", "").replace("Ph", "").strip()
            )
            raw_address = raw_address.split(";")[0].strip()
        else:
            phone = SgRecord.MISSING

        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            location_name=location_name,
            page_url=page_url,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="IN",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://in.sunglasshut.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
