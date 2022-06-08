import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://leon-nl.co/restaurants/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    js = json.loads(text)["props"]["initialReduxState"]["data"]["restaurants"]

    for j in js:
        a = j.get("locationDetails") or {}
        raw_address = a.get("fullAddress") or ""
        city = a.get("townOrCity") or ""
        postal = a.get("postCode")
        street_address = raw_address.split(f", {postal}")[0].strip()
        country_code = "NL"
        store_number = j.get("airshipId")
        location_name = j.get("name") or ""
        slug = j.get("slug")
        page_url = f"https://leon-nl.co/restaurants/{slug}"
        location_type = str(j.get("type")).capitalize()
        try:
            phone = j["contactDetails"]["phoneNumber"]
        except KeyError:
            phone = SgRecord.MISSING
        g = j.get("geoLocation") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")

        _tmp = []
        _days = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        try:
            hours = j["restaurantOpeningTimes"]["openingTimes"]
        except:
            hours = []

        for h in hours:
            day = h.get("day")
            _days.append(day)
            start = h.get("opensAt")
            end = h.get("closesAt")
            if start:
                _tmp.append(f"{day}: {start}-{end}")

        for day in days:
            if day not in _days:
                _tmp.append(f"{day}: Closed")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("Closed") == 7 or "Plaza" in location_name:
            continue

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://leon-nl.co/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
