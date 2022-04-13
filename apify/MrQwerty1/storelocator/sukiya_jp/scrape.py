from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://maps.sukiya.jp/la/api_shop.php"
    page_url = "https://www.sukiya.jp/en/locations/"
    r = session.get(api, headers=headers)
    js = r.json().values()
    for state in js:
        for city in state.values():
            for j in city.values():
                store_number = j.get("id")
                location_name = j["name"]["en"] or j["name"]["jp"]
                raw_address = j["address"]["en"] or j["address"]["jp"]
                street_address, city, state, postal = get_international(raw_address)
                if " " not in street_address:
                    street_address = " ".join(raw_address.split(", ")[:2])
                latitude = j.get("ido")
                longitude = j.get("keido")

                day = j["close"]["en"]
                inter = j["hours"]["en"]
                if day:
                    hours_of_operation = f"{day}: {inter}"
                else:
                    hours_of_operation = SgRecord.MISSING

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code="JP",
                    store_number=store_number,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.sukiya.jp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
