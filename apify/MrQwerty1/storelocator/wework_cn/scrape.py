from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_postal(line):
    adr = parse_address(International_Parser(), line)
    return adr.postcode or ""


def fetch_data(sgw: SgWriter):
    api = "https://api.wework.cn/chinaos/wwcnBackend/api/v2/buildings?"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        raw_address = j.get("address")
        postal = get_postal(raw_address)
        city = j.get("cityName") or ""
        state = j.get("divisionName") or ""
        street = (
            raw_address.replace(postal, "").replace(city, "").replace(state, "").strip()
        )
        if street.endswith(","):
            street = street[:-1]
        country_code = "CN"
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"https://www.wework.cn/en-US/building/{slug}"
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.wework.cn/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "locale": "en_US",
        "Origin": "https://www.wework.cn",
        "Connection": "keep-alive",
        "Referer": "https://www.wework.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
