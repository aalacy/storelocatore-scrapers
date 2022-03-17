from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.pingodoce.pt/wp-content/themes/pingodoce/ajax/pd-ajax.php?action=pd_stores_get_stores"
    r = session.get(api, headers=headers)
    js = r.json()["data"]["stores"]

    for j in js:
        location_name = j.get("name") or ""
        location_name = location_name.replace("&amp;", "&")
        latitude = j.get("lat")
        longitude = j.get("long")
        phone = j.get("contact")
        page_url = j.get("permalink")
        store_number = j.get("id")
        street_address = f'{j.get("address")} {j.get("number") or ""}'.replace(
            "\n", " "
        ).strip()
        city = j.get("county")
        state = j.get("district")
        postal = j.get("postal_code") or ""
        postal = postal.split()[0]
        if postal.endswith("-"):
            postal = postal[:-1]

        _tmp = []
        try:
            hours = j["schedules"]["full"] or dict()
        except KeyError:
            hours = dict()

        for day, v in hours.items():
            start = v.get("morningOpen")
            end = v.get("morningClose")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PT",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pingodoce.pt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
