from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.roady.fr/storelocator/index/loadstore/"
    r = session.post(api, headers=headers, data=data)
    js = r.json()["storesjson"]
    black_list = {"Zone", "ZA", "La ", "("}

    for j in js:
        street_address = j.get("address") or ""
        if "<br>" in street_address:
            _tmp = []
            line = street_address.split("<br>")
            for li in line:
                for b in black_list:
                    if b in li:
                        break
                else:
                    _tmp.append(li)
            street_address = ", ".join(_tmp)

        city = j.get("city")
        postal = j.get("zipcode")
        country_code = "FR"
        store_number = j.get("storelocator_id")
        location_name = j.get("store_name")
        slug = j.get("rewrite_request_path")
        page_url = f"https://www.roady.fr/{slug}"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("horaires") or ""
        hours_of_operation = hours_of_operation.replace("<br>", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.roady.fr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.roady.fr",
        "Connection": "keep-alive",
        "Referer": "https://www.roady.fr/storelocator/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "curPage": "1",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
