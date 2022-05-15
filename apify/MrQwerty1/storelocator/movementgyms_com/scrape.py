import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://movementgyms.com/location-finder/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.gym_locations =')]/text()")
    )
    text = text.split("window.gym_locations =")[1].split("}];")[0] + "}]"
    js = json.loads(text)

    for j in js:
        try:
            a = j["address"]["street_address"]
        except KeyError:
            a = dict()
        adr1 = a.get("street_number") or ""
        adr2 = a.get("street_name") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state_short")
        postal = a.get("post_code")
        country_code = "US"
        store_number = j.get("blog_id")
        location_name = j.get("location_name")
        page_url = j.get("url")
        phone = j.get("phone_number")
        latitude = a.get("lat")
        longitude = a.get("lng")

        _tmp = []
        hours = j.get("hours") or []
        for h in hours:
            day = h.get("days") or ""
            if "May" in day:
                continue
            start = h.get("opening_time")
            end = h.get("closing_time")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp) or "Coming Soon"

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
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://movementgyms.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
