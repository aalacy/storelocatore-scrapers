import json5
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.ufcgym.com/_nuxt/430502678cae5485010c.js"
    r = session.get(api, headers=headers)
    text = r.text
    text = "[" + text.split("exports=[")[1].split("}]},,")[0].replace("!", "") + "}]"
    js = json5.loads(text)

    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip") or ""
        country_code = "US"
        if " " in postal:
            country_code = "CA"
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("code")
        page_url = f"https://www.ufcgym.com/locations/{slug}"
        phone = j.get("phone")
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
            state=state,
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
    locator_domain = "https://www.ufcgym.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
