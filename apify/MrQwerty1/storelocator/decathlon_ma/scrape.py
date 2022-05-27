import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.decathlon.ma/page/mes_magasins.html"
    r = session.get(api)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'store_marker.push(')]/text()")
    ).split("store_marker.push(")
    links = tree.xpath("//a[@class='card']/@href")

    for t in text:
        if '"lat"' not in t:
            continue
        j = json.loads(t.split(");")[0].replace("&quot;", "'"))
        location_name = j.get("title")
        phone = j.get("phone")
        if not phone:
            continue

        page_url = links.pop(0)
        raw_address = j.get("address") or ""
        line = raw_address.split(", ")
        postal = line.pop()
        city = line.pop()
        street_address = ", ".join(line).replace("&#039;", "'")
        store_number = page_url.split("/")[-1].split("-")[0]
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("hours") or "[]"
        hours = eval(hours)
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day, h in zip(days, hours):
            _tmp.append(f"{day}: {h[0]}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="MA",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.ma/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
