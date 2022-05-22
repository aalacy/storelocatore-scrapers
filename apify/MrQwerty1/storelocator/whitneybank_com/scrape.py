import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://maps.locations.hancockwhitney.com/api/getAsyncLocations?template=search&level=search&search=36037&radius=5000"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    source = r.json()["maplist"]
    tree = html.fromstring(source)
    text = "[" + "".join(tree.xpath("//text()"))[:-1] + "]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("location_name")
        page_url = j.get("url")
        street_address = f'{j.get("address_1")} {j.get("address_2") or ""}'.strip()
        city = j.get("city")
        state = j.get("region")
        postal = j.get("post_code")
        country_code = j.get("country")
        phone = j.get("local_phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("fid")
        location_type = j.get("Type_CS")

        _tmp = []
        text = j.get("hours_sets:primary") or "{}"
        h = json.loads(text).get("days") or {}
        for k, v in h.items():
            if type(v) == str:
                _tmp.append(f"{k}: {v}")
            else:
                start = v[0].get("open")
                end = v[0].get("close")
                _tmp.append(f"{k}: {start} - {end}")
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.hancockwhitney.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
