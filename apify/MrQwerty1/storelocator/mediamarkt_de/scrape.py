import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.mediamarkt.de/de/store/store-finder"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.__PRELOADED_STATE__ =')]/text()")
    )
    text = text.split("window.__PRELOADED_STATE__ =")[1].strip()[:-1]
    js = json.loads(text)["apolloState"].values()

    for j in js:
        if j.get("__typename") != "GraphqlStore":
            continue
        a = j.get("address") or {}
        adr1 = a.get("street") or ""
        adr2 = a.get("houseNumber") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        country_code = "DE"
        store_number = j.get("id")
        location_name = a.get("name")
        page_url = f"https://www.mediamarkt.de/de/store/neuwied-{store_number}"
        phone = j.get("phoneNumber")

        p = j.get("position") or {}
        latitude = p.get("lat")
        longitude = p.get("lng")

        _tmp = []
        days = [
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY",
            "SATURDAY",
            "SUNDAY",
        ]
        opening = set()
        try:
            hours = j["openingTimes"]["regular"]
        except:
            hours = []

        for h in hours:
            day = h.get("type")
            opening.add(day)
            start = h.get("start")
            end = h.get("end")
            _tmp.append(f"{day}: {start}-{end}")

        for day in days:
            if day not in opening:
                _tmp.append(f"{day}: Closed")

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
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mediamarkt.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
