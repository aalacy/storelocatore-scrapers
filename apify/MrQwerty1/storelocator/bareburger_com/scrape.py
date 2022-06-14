from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    headers = {"Client": "bareburger"}
    r = session.post("https://patron.lunchbox.io/v0/locations", headers=headers)

    for j in r.json():
        a = j.get("address")
        street_address = f"{a.get('street1')} {a.get('street2') or ''}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zip")
        if len(postal) == 6:
            postal = postal[1:]
        location_name = j.get("name")
        slug = j.get("slug") or location_name
        page_url = f"https://order.bareburger.com/location/{slug}"
        phone = j.get("phone").get("value") or "<MISSING>"
        loc = a.get("geo")
        latitude = loc.get("lat")
        longitude = loc.get("long")

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("hours") or []
        for h in hours:
            index = h.get("day")
            day = days[index]
            start = h.get("dineInOpen")
            close = h.get("dineInClose")
            _tmp.append(f"{day}: {start} - {close}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://bareburger.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
