from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.vodafone.hu/api/content/applications/shoplocator/shops"
    page_url = "https://www.vodafone.hu/english/shoplocator"
    r = session.get(api, headers=headers)
    js = r.json()["content"].values()

    for j in js:
        location_name = j.get("name")
        store_number = j.get("id")

        g = j.get("geoLocation") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")

        a = j.get("detailedAddress") or {}
        street_address = f'{a.get("publicAreaName")} {a.get("publicAreaType")} {a.get("number")}'.replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("zipCode")

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
        hours = j.get("openingHour") or []
        for d, h in zip(days, hours):
            start = h.get("startTime")
            if start == "Zárva":
                _tmp.append(f"{d}: Zárva")
                continue
            end = h.get("endTime")
            _tmp.append(f"{d}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="HU",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.hu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
