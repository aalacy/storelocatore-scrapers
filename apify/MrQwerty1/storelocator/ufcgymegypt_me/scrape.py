import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_js():
    r = session.get("https://www.ufcgym.me/locations/list/", headers=headers)
    tree = html.fromstring(r.text)
    scripts = tree.xpath("//script[contains(@src, '_nuxt')]/@src")

    for s in scripts:
        r = session.get(f"https://www.ufcgym.me{s}")
        text = r.text
        if "JSON.parse('" not in text or "FRANCHISE" not in text:
            continue

        text = text.split("JSON.parse('")[1].split("}]')}")[0] + "}]"
        js = json5.loads(text)
        return js


def fetch_data(sgw: SgWriter):
    js = get_js()

    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("zip") or ""
        postal = postal.strip()
        country_code = j.get("state")
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("code")
        page_url = f"https://www.ufcgym.me/locations/{slug}"
        phone = j.get("phone") or ""
        if "GYM" in phone:
            phone = SgRecord.MISSING
        location_type = j.get("type")

        p = j.get("position") or {}
        latitude = p.get("lat")
        longitude = p.get("lng")

        _tmp = []
        hours = j.get("hours") or []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        for day, inter in zip(days, hours):
            if "SOON" in inter:
                _tmp.append("Coming Soon")
                break
            _tmp.append(f"{day}: {inter}")

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
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.ufcgym.me/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
