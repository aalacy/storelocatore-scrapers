import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.greasemonkeyauto.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1&category=87%2C86%2C85%2C84%2C83%2C82%2C81%2C80%2C79%2C78%2C77%2C76%2C75%2C74%2C73%2C72%2C71%2C70%2C69%2C68%2C67%2C66%2C65%2C64%2C63%2C62%2C61%2C60%2C58%2C57%2C56%2C55%2C53%2C132%2C143"
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("title")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        store_number = j.get("id")
        slug = j.get("website") or ""
        page_url = f"https://www.greasemonkeyauto.com/{slug}"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("open_hours") or ""
        hours = json.loads(hours)

        for k, v in hours.items():
            if v == "0" or v[0] == " - ":
                _tmp.append(f"{k.capitalize()}: Closed")
            else:
                _tmp.append(f"{k.capitalize()}: {v[0]}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.greasemonkeyauto.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
    }

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
