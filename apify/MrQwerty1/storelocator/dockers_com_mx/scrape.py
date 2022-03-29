from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_city(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or SgRecord.MISSING

    return city


def fetch_data(sgw: SgWriter):
    api = "https://www.dockers.com.mx/api/dataentities/SF/search?_fields=client,store,address,phone,lat,lng,state,whatsapp&_schema=store-finder&_sort=state%20ASC"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        raw_address = j.get("address") or ""
        street_address = raw_address.split(",")[0].strip()
        if "Col." in raw_address:
            city = raw_address.split("Col.")[1].split(",")[0].strip()
            street_address = raw_address.split("Col.")[0].strip()
        else:
            city = raw_address.split(",")[1].strip()

        city = get_city(city)
        state = j.get("state")
        country_code = "MX"
        location_name = j.get("store")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.dockers.com.mx/"
    page_url = "https://www.dockers.com.mx/tiendas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/vnd.vtex.ds.v10+json",
        "Referer": "https://www.dockers.com.mx/tiendas",
        "REST-Range": "resources=0-2000",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
