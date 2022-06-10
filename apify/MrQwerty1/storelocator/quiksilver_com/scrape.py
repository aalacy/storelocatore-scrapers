from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.quiksilver.com/on/demandware.store/Sites-QS-US-Site/en_US/StoreLocator-StoreLookup"
    r = session.get(api, headers=headers, params=params)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        street_address = j.get("address") or ""
        street_address = " ".join(street_address.split())
        city = j.get("city") or ""
        state = j.get("state") or ""
        postal = j.get("postalCode") or ""
        street_address = street_address.replace("-", "").strip()
        postal = postal.replace("-", "").strip()
        raw_address = " ".join(f"{street_address} {city} {state} {postal}".split())
        country = j.get("country")
        phone = j.get("phone") or ""
        phone = phone.replace("NEW", "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("ID")

        _tmp = []
        hours = j.get("storeHours") or []
        for h in hours:
            day = h[0]
            start = h[1]
            end = h[-2]
            if start:
                _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.quiksilver.com/"
    page_url = "https://www.quiksilver.com/stores/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    params = (
        ("latitude", "51.47409884876886"),
        ("longitude", "59.34291712788323"),
        ("mapRadius", "20000"),
    )

    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
