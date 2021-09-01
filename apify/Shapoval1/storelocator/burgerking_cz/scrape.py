from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.cz/"
    api_url = "https://bkcz.api.amdv.amrest.eu/ordering-api/rest/v2/restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "cs",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Source": "WEB",
        "Origin": "https://burgerking.cz",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJhNDg5ZDRjZi00YTI3LTRjNTItOTg5YS0xZTIxZWM0YWRjZTFcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIk1PQklMRV9QSF9BTkRST0lEXCIsXCJleHBpcmlhdGlvbkRhdGVcIjoxNjU4OTAwNjk3MjgzLFwiZW5hYmxlZFwiOnRydWUsXCJhY2NvdW50Tm9uTG9ja2VkXCI6dHJ1ZSxcImNyZWRlbnRpYWxzTm9uRXhwaXJlZFwiOnRydWUsXCJhY2NvdW50Tm9uRXhwaXJlZFwiOnRydWV9In0.t9JEdh6i1effd65QSZFYW2CjmO0o_tLCiSowOmnIzG7xRhPSGguA92-Sc0plF-BGn-ydiPBMPbeUT3POXM3_7g",
        "Referer": "https://burgerking.cz/",
        "Connection": "keep-alive",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["restaurants"]
    for j in js:

        page_url = "https://burgerking.cz/restaurants"
        location_name = j.get("name")
        location_type = j.get("restaurantType")
        street_address = f"{j.get('addressStreetNo')} {j.get('addressStreet')}".strip()
        postal = j.get("addressPostalCode")
        country_code = "Czech Republic"
        city = j.get("addressCity")
        store_number = j.get("id")
        latitude = j.get("geoLat")
        longitude = j.get("geoLng")

        session = SgRequests()
        r = session.get(
            f"https://bkcz.api.amdv.amrest.eu/ordering-api/rest/v1/restaurants/{store_number}/TAKEOUT",
            headers=headers,
        )
        js = r.json()["details"]

        phone = js.get("phoneNo")
        hours_of_operation = f"Mon {js.get('openMonFrom')} - {js.get('openMonTo')} Tue {js.get('openTueFrom')} - {js.get('openTueTo')} Wed {js.get('openWedFrom')} - {js.get('openWedTo')} Thu {js.get('openThuFrom')} - {js.get('openThuTo')} Fri {js.get('openFriFrom')} - {js.get('openFriTo')} Sat {js.get('openSatFrom')} - {js.get('openSatTo')} Sun {js.get('openSunFrom')} - {js.get('openSunTo')}"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
