import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.paul-indonesia.co.id/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=2&layout=1&nw[]=-4.775482044562745&nw[]=104.62260607499996&se[]=-7.669391923238669&se[]=109.01713732499996"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("title")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        phone = j.get("phone") or ""
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")

        _tmp = []
        text = j.get("open_hours") or ""
        try:
            hours = json.loads(text)
        except:
            hours = dict()

        for day, v in hours.items():
            if isinstance(v, list):
                inter = "".join(v)
            else:
                inter = "Closed"
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ID",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul-indonesia.co.id/"
    page_url = "https://www.paul-indonesia.co.id/en/our-store/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.paul-indonesia.co.id/en/our-store/",
    }
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
