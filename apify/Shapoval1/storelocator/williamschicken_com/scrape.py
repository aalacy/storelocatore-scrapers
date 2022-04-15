from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://williamschicken.com"
    api_url = "https://williamschicken.com/wcnewwp/wp-admin/admin-ajax.php?action=store_search&lat=32.77666&lng=-96.79699&max_results=5&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://williamschicken.com/locations/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("permalink") or "https://williamschicken.com/locations/"
        location_name = j.get("store") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = location_name.split("#")[1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = j.get("store_custom_message") or "<MISSING>"
        if hours_of_operation == "Seasonal" or hours_of_operation == "Call for Hours":
            hours_of_operation = "<MISSING>"

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
