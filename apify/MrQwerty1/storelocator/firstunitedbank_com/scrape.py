from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.firstunitedbank.com/q2_map/ajax/get-location-data/1"
    r = session.get(api)
    js = r.json()["locations"]

    for j in js:
        location_name = j.get("name") or ""
        page_url = j.get("url")
        _types = j.get("type") or []
        if "Drive" in location_name:
            _types.append("Drive-Thru")
        location_type = ", ".join(_types)
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("long")

        _tmp = []
        source = j.get("hours") or "<html/>"
        tree = html.fromstring(source)
        tr = tree.xpath("//tr[not(./td[2]/strong)]")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            inter = "".join(t.xpath("./td[2]//text()")).strip()
            if "Drive-Thru" in _types:
                inter = "".join(t.xpath("./td[3]//text()")).strip()
            if inter == "N/A":
                continue
            _tmp.append(f"{day}: {inter}")

        hours_of_operations = ";".join(_tmp)
        if not hours_of_operations and "soon" in source:
            hours_of_operations = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            hours_of_operation=hours_of_operations,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.firstunitedbank.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
