import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//span[@class='number']/text()"))


def fetch_data(sgw: SgWriter):
    api = "https://www.ko2go.co.uk/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var branches =')]/text()")
    ).strip()
    text = text.split("var branches =")[1].split("}];")[0] + "}]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("name")
        slug = j.get("alias")
        page_url = f"https://www.ko2go.co.uk/{slug}/"
        phone = get_phone(page_url)
        street_address = j.get("address1")
        city = j.get("name")
        postal = j.get("postcode")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("id")

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
        hours = j.get("opening_times") or []
        for h in hours:
            index = h.get("day_of_week")
            if not index:
                continue
            day = days[int(index) - 1]
            note = h.get("custom_note")
            if note:
                _tmp.append(f"{day}: {note}")
                continue
            start = h.get("from_time")
            end = h.get("to_time")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.kebabishoriginal.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
