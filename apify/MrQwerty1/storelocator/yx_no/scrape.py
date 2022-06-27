from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def clean_phone(text):
    _tmp = []
    for t in text:
        if t.isdigit():
            _tmp.append(t)

    return "".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://meilisearch.yx.no/indexes/stations/search"
    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["hits"]

    for j in js:
        street_address = j.get("address")
        city = j.get("place")
        postal = j.get("zipcode")
        country = j.get("country")
        if country == "Norway":
            country_code = "NO"
        elif country == "Denmark":
            country_code = "DK"
        else:
            country_code = "SE"

        store_number = j.get("id")
        location_name = j.get("name")
        phone = j.get("phone") or ""
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        phone = clean_phone(phone)
        location_type = j.get("chain")

        g = j.get("_geo") or {}
        latitude = g.get("lat") or "0"
        longitude = g.get("lng")

        if str(latitude) == "0":
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://yx.no/"
    page_url = "https://yx.no/kart/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://yx.no/",
        "X-Meili-API-Key": "cda56406d550585ce01807040c54ad1614aca7bc81e42d9872633b3c194eeabe",
        "Origin": "https://yx.no",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    json_data = {
        "facetsDistribution": [
            "tags",
            "chain",
            "fuel",
            "other",
        ],
        "attributesToHighlight": [
            "*",
        ],
        "limit": 2000,
        "q": "",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
