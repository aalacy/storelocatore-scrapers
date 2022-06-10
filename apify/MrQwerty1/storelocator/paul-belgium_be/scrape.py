import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://shop.paul-belgium.be/nl/bakkerijen?redirect=%2Fnl%2Fproducten"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'window.esign.info')]/text()"))
    text = text.split('"locations":')[1].split("}]};")[0] + "}]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("name")
        store_number = j.get("id")
        page_url = f"https://shop.paul-belgium.be/nl/bakkerijen?redirect=%2Fnl%2Fproducten#location-{store_number}"
        street_address = f'{j.get("street")} {j.get("street_number") or ""}'.strip()
        city = j.get("town")
        postal = j.get("postal")

        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = j.get("hours") or []
        cnt = 1
        for day in days:
            for h in hours:
                if h.get("day") == cnt:
                    start = h.get("from")
                    end = h.get("to")
                    _tmp.append(f"{day}: {start}-{end}")
                    break
            else:
                _tmp.append(f"{day}: Closed")
            cnt += 1

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="BE",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://paul-belgium.be/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
