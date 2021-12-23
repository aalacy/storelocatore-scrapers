from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(
        "https://api.tuffshed.io/sites/Sites/search?SiteTypes=1&SiteTypes=2&SiteTypes=3&SiteTypes=8",
        headers=headers,
    )
    page_url = "https://www.tuffshed.com/locate/"

    for j in r.json():
        if not j.get("active"):
            continue
        location_name = j.get("name") or ""
        g = j.get("siteCoordinates") or {}
        latitude = g.get("siteLatitude")
        longitude = g.get("siteLongitude")
        store_number = location_name.split("-")[0].strip()
        a = j.get("address") or {}
        street_address = a.get("street")
        city = a.get("city")
        state = a.get("stateProvince")
        postal = a.get("postalCode")
        country_code = "US"
        try:
            phone = j["phoneNumbers"][0]["number"]
        except:
            phone = SgRecord.MISSING

        hours = j.get("openingHours") or []
        hours_of_operation = ";".join(hours)
        if not hours_of_operation and not latitude:
            continue
        if not hours_of_operation:
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.tuffshed.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik1yNS1BVWliZkJpaTdOZDFqQmViYXhib1hXMCIsImtpZCI6Ik1yNS1BVWliZkJpaTdOZDFqQmViYXhib1hXMCJ9.eyJhdWQiOiJhcGk6Ly9hcGkucHJkLnR1ZmZzaGVkLmlvIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvZTY5MzAwZGUtZjQ5NC00Y2Y2LTliMmMtMTVlNzA2MzY2Y2Q5LyIsImlhdCI6MTY0MDE4OTU0OCwibmJmIjoxNjQwMTg5NTQ4LCJleHAiOjE2NDAxOTM0NDgsImFpbyI6IkUyWmdZR2dPOGc4Uk1ESTU5dkp3dGtIOGN2ZXRBQT09IiwiYXBwaWQiOiI5YzM3Njc4ZS0wOTc4LTQ2M2MtOGY1Ny0wOTFlMWQ1NDdkZjciLCJhcHBpZGFjciI6IjEiLCJncm91cHMiOlsiY2M3YThhYWYtNjQ2Ni00NjRiLTlkOTMtZTM4ZWQ5MWZiOWUxIiwiOWJjNjczNDEtMDZiOS00YmNiLWFmMWItMGNkYzYxMWNlYjQxIl0sImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2U2OTMwMGRlLWY0OTQtNGNmNi05YjJjLTE1ZTcwNjM2NmNkOS8iLCJvaWQiOiJkNzkxZmMzNi1mOGVhLTQ4MjgtOGE4Mi0zYzhlOGZjYWIyNzgiLCJyaCI6IjAuQVRnQTNnQ1Q1cFQwOWt5YkxCWG5CalpzMlk1bk41eDRDVHhHajFjSkhoMVVmZmM0QUFBLiIsInN1YiI6ImQ3OTFmYzM2LWY4ZWEtNDgyOC04YTgyLTNjOGU4ZmNhYjI3OCIsInRpZCI6ImU2OTMwMGRlLWY0OTQtNGNmNi05YjJjLTE1ZTcwNjM2NmNkOSIsInV0aSI6InRwWlQtcU1xdWtpeEtleTUwMEJhQUEiLCJ2ZXIiOiIxLjAifQ.ru2R_OjGjdeh8Yj6sD5SJCW5eamHmGORGDPIBt24b1GgvxBnRFnEyvwt1e6h_XmTShxxY-UPivF7M41_11ZIm9iMtvU3xHrtomCDAOqLEa_VUMPNRGeWGf3VPiKM9xsg0xi0APcWayuBbd2jTaFFCZtyyLnBPf3v1CTG5sftceg98Vml9frjM9uoxwam_I22a3wgywesw6d5YtxDw_oEZA_ap_pOG6iMNJ6aAd3nmDZr9XI0HuaSnx8gD7C0l5yTvGC-0KnR9lt9ZciWpvEqTGzFyNJPJ6nyIdeWO87KmPR3XFA6gaDXu75AcGkwITiTEiY0eOwQbxsOGePhVXxmGQ",
        "Origin": "https://www.tuffshed.com",
        "Connection": "keep-alive",
        "Referer": "https://www.tuffshed.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
