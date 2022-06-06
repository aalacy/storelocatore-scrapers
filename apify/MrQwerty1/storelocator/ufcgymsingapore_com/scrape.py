from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    phone = "".join(tree.xpath("//span[contains(text(), '+')]/text()")).strip()
    if "/" in phone:
        phone = phone.split("/")[0].strip()

    hoo = ";".join(tree.xpath("//span[contains(text(), ':')]/text()"))

    return phone, hoo


def fetch_data(sgw: SgWriter):
    api = (
        "https://www.ufcgymsingapore.com/_api/cloud-data/v1/wix-data/collections/query"
    )
    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["items"]

    for j in js:
        m = j.get("mapLocation") or {}
        s = m.get("streetAddress") or {}
        raw_address = m.get("formatted")
        adr1 = s.get("number") or ""
        adr2 = s.get("name") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = m.get("city")
        postal = m.get("postalCode")
        country_code = m.get("country")
        location_name = j.get("title") or ""
        slug = location_name.replace("UFC GYM", "").strip().lower().replace(" ", "-")
        page_url = f"https://www.ufcgymsingapore.com/{slug}"

        g = m.get("location") or {}
        latitude = g.get("latitude")
        longitude = g.get("longitude")

        phone, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.ufcgymsingapore.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "authorization": "wixcode-pub.e68de599033da6d8f17f94ee66c7c1b6508debdb.eyJpbnN0YW5jZUlkIjoiNDk2NDUxYTUtYzMyMy00OWVlLThlMTMtMTMxMGJiMDU1OWM2IiwiaHRtbFNpdGVJZCI6ImZmMWU1NDc3LTFmOGItNGYyNS05MTYxLWQ5ZjFlOTJlYTgzYyIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTY1MDQ0MDE2MzM4MywiYWlkIjoiMjFiYjE2M2MtYzBjNi00OTgwLThjNTctMWRhMmE2YzVmMjRmIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjA0ZjZlMTk0LTkwNTEtNDI4ZC04NWNiLTJiYmU4MWJhMzc1YiIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsSGFzRG9tYWluLFNob3dXaXhXaGlsZUxvYWRpbmciLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiNjJlNmQyZWItYmJkOS00MWE5LTg2YWUtNjAyOGJjMzE4ODRhIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==",
    }

    json_data = {
        "collectionName": "Locations",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
