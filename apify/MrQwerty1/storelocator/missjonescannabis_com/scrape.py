from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://locations-service.api.unoapp.io/clients/businesses/f03251d1-ba69-4d0c-a1de-c2e0f734c48e/locations/search/nearby"
    r = session.get(api, headers=headers, params=params)
    js = r.json()["payload"]

    for j in js:
        a = j.get("address") or {}
        raw_address = a.get("formatted_address") or ""
        adr1 = a.get("address_line_1") or ""
        adr2 = a.get("address_line_2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = raw_address.split(", ")[-2].split()[0]
        postal = a.get("postal_code")
        country_code = "CA"
        store_number = j.get("id")
        location_name = j.get("display_name")
        slug = adr1.replace(" ", "-").lower()
        page_url = f"https://missjonescannabis.com/outposts/{slug}"
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        phone = SgRecord.MISSING
        details = j.get("contact_details") or []
        for d in details:
            if d.get("type") == "phone":
                phone = d.get("value")
                break

        _tmp = []
        hours = j.get("hours_of_operation") or []
        for h in hours:
            day = h.get("day_name")
            start = str(h.get("open_time")).rsplit(":00", 1).pop(0)
            end = str(h.get("close_time")).rsplit(":00", 1).pop(0)
            if start == end:
                _tmp.append(f"{day}: Closed")
                continue
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("Closed") == 7:
            page_url = page_url.replace("/outposts/", "/shop/")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://missjonescannabis.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "api-token": "b09172c4e50751f49bf00180aa0cd3b7b24d3f0e",
        "auth-token": "",
        "Origin": "https://budler.ca",
        "Connection": "keep-alive",
        "Referer": "https://budler.ca/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    params = {
        "lat": "41.6284672",
        "long": "41.6120832",
        "radius": "500000",
        "operation_hours": "true",
        "address": "true",
        "contact_details": "true",
        "settings": "true",
        "images": "true",
        "delivery_hours": "false",
        "timeslots": "false",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
