import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://maxbrenner.com.au/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        adr1 = j.get("street") or ""
        adr2 = j.get("street2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "AU"
        store_number = j.get("id")
        location_name = j.get("title") or ""
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        source = j.get("open_hours") or "{}"
        hours = json.loads(source)
        for day, i in hours.items():
            if isinstance(i, list):
                _tmp.append(f'{day}: {"&".join(i)}')

        hours_of_operation = ";".join(_tmp)
        if "temporarily" in location_name.lower():
            hours_of_operation = "Temporarily Closed"

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://maxbrenner.com.au/"
    page_url = "https://maxbrenner.com.au/find-a-dessert-bar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
