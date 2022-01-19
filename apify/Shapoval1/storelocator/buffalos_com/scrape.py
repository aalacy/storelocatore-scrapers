import httpx
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://buffalos.com/"
        api_url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=ZUTSSFQCGXCOLGAT&multi_account=false"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        js = r.json()["locations"]

        for j in js:

            slug = j.get("llp_url")
            page_url = f"https://locations.buffalos.com{slug}"
            a = j.get("store_info")
            street_address = f"{a.get('address')} {a.get('address_extended')}".strip()
            if street_address.find("Ezdan") != -1:
                continue
            state = a.get("region") or "<MISSING>"
            postal = a.get("postcode")
            country_code = a.get("country")
            city = a.get("locality")
            cms = j.get("open_or_closed")
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Authorization": "ZUTSSFQCGXCOLGAT",
                "Origin": "https://locations.buffalos.com",
                "Connection": "keep-alive",
                "Referer": "https://locations.buffalos.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "Cache-Control": "max-age=0",
                "TE": "trailers",
            }
            slug = a.get("address")
            params = (
                ("address", f"{slug}"),
                ("locality", f"{city}"),
                ("multi_account", "false"),
                ("pageSize", "30"),
                ("region", f"{state}"),
            )
            r = http.get(
                url="https://api.momentfeed.com/v1/analytics/api/llp.json",
                headers=headers,
                params=params,
            )
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            js = r.json()
            for j in js:

                aa = j.get("store_info")
                latitude = aa.get("latitude") or "<MISSING>"
                longitude = aa.get("longitude") or "<MISSING>"
                location_name = aa.get("name") or "<MISSING>"
                location_type = aa.get("brand_name") or "<MISSING>"
                phone = aa.get("phone") or "<MISSING>"
                hours_of_operation = (
                    str(aa.get("store_hours"))
                    .replace("1,", "Monday ")
                    .replace("2,", "Tuesday ")
                    .replace("3,", "Wednesday ")
                    .replace("4,", "Thursday ")
                    .replace("5,", "Friday ")
                    .replace("6,", "Saturday ")
                    .replace("7,", "Sunday ")
                    .strip()
                )
                hours_of_operation = (
                    hours_of_operation.replace("0000,0000;", "Open 24 Hours ")
                    .replace("00,", ":00 - ")
                    .replace("30,", ":30 - ")
                    .replace("00;", ":00 ")
                    .replace("30;", ":30 ")
                )
                hours_of_operation = hours_of_operation or "<MISSING>"
                if cms == "coming soon":
                    hours_of_operation = "coming soon"
                if cms == "closed":
                    hours_of_operation = "closed"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=f"{street_address} {city}, {state} {postal}",
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
