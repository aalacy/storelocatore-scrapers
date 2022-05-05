from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.pl/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "pl",
        "Referer": "https://burgerking.pl/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NzgwMTI5NjcxMzEsXCJlbmFibGVkXCI6dHJ1ZSxcImFjY291bnROb25Mb2NrZWRcIjp0cnVlLFwiY3JlZGVudGlhbHNOb25FeHBpcmVkXCI6dHJ1ZSxcImFjY291bnROb25FeHBpcmVkXCI6dHJ1ZX0ifQ.XQaoqEQjo4pSYTIvJ-deC9T4TuBEw6tkm9FIXohULlRZO6nVv5Bp5bCtg6IzEyHg-b3nzfh2FJLoDdkBph4kuQ",
        "Source": "WEB",
        "Origin": "https://burgerking.pl",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    r = session.get(
        "https://bkpl.api.amdv.amrest.eu/ordering-api/rest/v2/restaurants/",
        headers=headers,
    )
    js = r.json()["restaurants"]
    for j in js:

        page_url = "https://burgerking.pl/pl/restaurants"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("restaurantType") or "<MISSING>"
        street_address = (
            f"{j.get('addressStreetNo')} {j.get('addressStreet')}".strip()
            or "<MISSING>"
        )
        state = "<MISSING>"
        postal = j.get("addressPostalCode") or "<MISSING>"
        country_code = "US"
        city = j.get("addressCity") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("geoLat") or "<MISSING>"
        longitude = j.get("geoLng") or "<MISSING>"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "pl",
            "Referer": "https://burgerking.pl/",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NzgwMTI5NjcxMzEsXCJlbmFibGVkXCI6dHJ1ZSxcImFjY291bnROb25Mb2NrZWRcIjp0cnVlLFwiY3JlZGVudGlhbHNOb25FeHBpcmVkXCI6dHJ1ZSxcImFjY291bnROb25FeHBpcmVkXCI6dHJ1ZX0ifQ.XQaoqEQjo4pSYTIvJ-deC9T4TuBEw6tkm9FIXohULlRZO6nVv5Bp5bCtg6IzEyHg-b3nzfh2FJLoDdkBph4kuQ",
            "Source": "WEB",
            "Origin": "https://burgerking.pl",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

        r = session.get(
            f"https://bkpl.api.amdv.amrest.eu/ordering-api/rest/v1/restaurants/{store_number}/TAKEOUT",
            headers=headers,
        )
        js = r.json()["details"]
        phone = js.get("phoneNo")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tmp = []
        for d in days:
            day = d
            opens = js.get(f"open{d}From")
            closes = js.get(f"open{d}To")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
