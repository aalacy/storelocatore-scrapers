import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    if len(street) < 3:
        street = line.split(",")[0].strip()

    return street


def fetch_data(sgw: SgWriter):
    api = "https://leon.co/all-restaurants/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    js = json.loads(text)["props"]["initialReduxState"]["data"]["restaurants"]

    for j in js:
        a = j.get("locationDetails") or {}
        raw_address = a.get("fullAddress")
        street_address = get_street(raw_address)
        city = a.get("townOrCity")
        postal = a.get("postCode")
        country_code = "GB"
        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"https://leon.co/restaurants/{slug}"
        c = j.get("contactDetails") or {}
        phone = c.get("phoneNumber") or ""
        if "on" in phone:
            phone = phone.split("on")[-1].strip()
        location_type = j.get("type")
        g = j.get("geoLocation") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")

        _tmp = []
        hr = j.get("restaurantOpeningTimes") or {}
        if hr.get("closed"):
            _tmp.append("Closed")
        hours = hr.get("openingTimes") or []
        inters = dict()
        for h in hours:
            day = h.get("day")
            start = ":".join(str(h.get("opensAt")).split(":")[:2])
            end = h.get("closesAt")
            inters[day] = {"inter": f"{start}-{end}"}

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            inter = inters.get(day)
            if inter:
                _tmp.append(f'{day}: {inter["inter"]}')
            else:
                _tmp.append(f"{day}: Closed")

        hours_of_operation = ";".join(_tmp)

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://leon.co/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
