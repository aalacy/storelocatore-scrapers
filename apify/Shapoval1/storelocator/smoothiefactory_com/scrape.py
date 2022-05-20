from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://smoothiefactory.com/"
    api_url = "https://locations.smoothiefactory.com/scripts/app-2765b7146c.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    token = r.text.split('"API_TOKEN",')[1].split(")")[0].replace('"', "").strip()
    r = session.get(
        f"https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token={token}&multi_account=false",
        headers=headers,
    )
    js = r.json()["locations"]
    for j in js:
        a = j.get("store_info")
        slug = j.get("llp_url")
        page_url = f"https://locations.smoothiefactory.com{slug}"
        street_address = f"{a.get('address')} {a.get('address_extended')}".strip()
        state = a.get("region")
        postal = a.get("postcode")
        country_code = a.get("country")
        city = a.get("locality")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Authorization": f"{token}",
            "Origin": "https://locations.smoothiefactory.com",
            "Connection": "keep-alive",
            "Referer": "https://locations.smoothiefactory.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Cache-Control": "max-age=0",
            "TE": "trailers",
        }

        params = (
            ("address", f'{a.get("address")}'),
            ("locality", f"{city}"),
            ("multi_account", "false"),
            ("pageSize", "30"),
            ("region", f"{state}"),
        )

        r = session.get(
            "https://api.momentfeed.com/v1/analytics/api/llp.json",
            headers=headers,
            params=params,
        )
        j = r.json()[0]
        b = j.get("store_info")
        cls = j.get("open_or_closed")
        location_name = b.get("name")
        latitude = b.get("latitude") or "<MISSING>"
        longitude = b.get("longitude") or "<MISSING>"
        phone = b.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(b.get("store_hours"))
            .replace("1,", "Monday ")
            .replace("2,", "Tuesday ")
            .replace("3,", "Wednesday ")
            .replace("4,", "Thursday ")
            .replace("5,", "Friday ")
            .replace("6,", "Saturday ")
            .replace("7,", "Sunday ")
            .replace("00,", ":00-")
            .replace("30,", ":30-")
            .replace("00;", ":00 ")
            .replace("30;", ":30 ")
            .strip()
        )
        if cls == "temp closed":
            hours_of_operation = "Temporarily Closed"

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
            location_type=SgRecord.MISSING,
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
