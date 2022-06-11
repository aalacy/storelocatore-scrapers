from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dostava.kfc.rs/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "sr",
        "Referer": "https://kfc.rs/",
        "Content-Type": "application/json; charset=UTF-8",
        "Brand": "KFC",
        "Origin": "https://kfc.rs",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2ODAwODAyOTI5OTcsXCJlbmFibGVkXCI6dHJ1ZSxcImFjY291bnROb25Mb2NrZWRcIjp0cnVlLFwiY3JlZGVudGlhbHNOb25FeHBpcmVkXCI6dHJ1ZSxcImFjY291bnROb25FeHBpcmVkXCI6dHJ1ZX0ifQ.s5chlX6KtiH4dU0n9Mzd_bDQDX6TiSeemL-67W9lzqMyPS7kf6kvGsRAJa2YoDxFrmfRprdKz1nbItnAmFejhQ",
        "Connection": "keep-alive",
    }

    r = session.get(
        "https://api.amrest.eu/amdv/ordering-api/KFC_RS/rest/v2/restaurants/",
        headers=headers,
    )
    js = r.json()["restaurants"]
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('addressStreetNo')} {j.get('addressStreet')}".replace(
            "None", ""
        ).strip()
        postal = j.get("addressPostalCode") or "<MISSING>"
        country_code = "RS"
        city = j.get("addressCity") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = f"https://kfc.rs/main/home/restaurant/{store_number}"
        latitude = j.get("geoLat") or "<MISSING>"
        longitude = j.get("geoLng") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "sr",
            "Referer": "https://kfc.rs/",
            "Source": "WEB",
            "Content-Type": "application/json; charset=UTF-8",
            "Brand": "KFC",
            "Origin": "https://kfc.rs",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2ODAwODAyOTI5OTcsXCJlbmFibGVkXCI6dHJ1ZSxcImFjY291bnROb25Mb2NrZWRcIjp0cnVlLFwiY3JlZGVudGlhbHNOb25FeHBpcmVkXCI6dHJ1ZSxcImFjY291bnROb25FeHBpcmVkXCI6dHJ1ZX0ifQ.s5chlX6KtiH4dU0n9Mzd_bDQDX6TiSeemL-67W9lzqMyPS7kf6kvGsRAJa2YoDxFrmfRprdKz1nbItnAmFejhQ",
            "Connection": "keep-alive",
        }

        r = session.get(
            f"https://api.amrest.eu/amdv/ordering-api/KFC_RS/rest/v2/restaurants/details/{store_number}",
            headers=headers,
        )
        js = r.json()["details"]
        phone = js.get("phoneNo") or "<MISSING>"
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = js.get("facilityOpenHours")

        tmp = []
        if hours:
            for d in days:
                day = d
                opens = hours.get(f"openHours{d}")[0].get("openFrom")
                closes = hours.get(f"openHours{d}")[0].get("openTo")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
