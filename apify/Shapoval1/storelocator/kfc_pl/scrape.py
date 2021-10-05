from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfc.pl"
    api_url = "https://kfcdostawa.pl/ordering-api/rest/v2/restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en",
        "Referer": "https://kfc.pl/",
        "Content-Type": "application/json; charset=UTF-8",
        "Brand": "KFC",
        "Origin": "https://kfc.pl",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NTgwNDc4NTA4NDcsXCJhY2NvdW50Tm9uTG9ja2VkXCI6dHJ1ZSxcImNyZWRlbnRpYWxzTm9uRXhwaXJlZFwiOnRydWUsXCJhY2NvdW50Tm9uRXhwaXJlZFwiOnRydWUsXCJlbmFibGVkXCI6dHJ1ZX0ifQ.SxqRI0ocXt0R4mYMK6m1A4VDn0KA97XNaRkRTDXqR7tySqkPcCT-l01epLUFdv-HqKl2PIMnPDGffsoHko0Mow",
        "Connection": "keep-alive",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["restaurants"]
    for j in js:
        page_url = "https://kfc.pl/main/home/restaurants"
        location_name = j.get("name")
        location_type = j.get("restaurantType")
        street_address = f"{j.get('addressStreetNo')} {j.get('addressStreet')}"
        postal = j.get("addressPostalCode")
        country_code = "PL"
        city = j.get("addressCity")
        store_number = j.get("id")
        latitude = j.get("geoLat")
        longitude = j.get("geoLng")

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en",
            "Referer": "https://kfc.pl/",
            "Source": "WEB",
            "Content-Type": "application/json; charset=UTF-8",
            "Brand": "KFC",
            "Origin": "https://kfc.pl",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NTgwNDc4NTA4NDcsXCJhY2NvdW50Tm9uTG9ja2VkXCI6dHJ1ZSxcImNyZWRlbnRpYWxzTm9uRXhwaXJlZFwiOnRydWUsXCJhY2NvdW50Tm9uRXhwaXJlZFwiOnRydWUsXCJlbmFibGVkXCI6dHJ1ZX0ifQ.SxqRI0ocXt0R4mYMK6m1A4VDn0KA97XNaRkRTDXqR7tySqkPcCT-l01epLUFdv-HqKl2PIMnPDGffsoHko0Mow",
            "Connection": "keep-alive",
        }
        r = session.get(
            f"https://kfcdostawa.pl/ordering-api/rest/v1/restaurants/details/{store_number}",
            headers=headers,
        )
        js = r.json()["details"]

        phone = js.get("phoneNo")
        h = js.get("facilityOpenHours")
        hours_of_operation = f"Mon {h.get('openMonFrom')} - {h.get('openMonTo')} Tue {h.get('openTueFrom')} - {h.get('openTueTo')} Wed {h.get('openWedFrom')} - {h.get('openWedTo')} Thu {h.get('openThuFrom')} - {h.get('openThuTo')} Fri {h.get('openFriFrom')} - {h.get('openFriTo')} Sat {h.get('openSatFrom')} - {h.get('openSatTo')} Sun {h.get('openSunFrom')} - {h.get('openSunTo')}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
