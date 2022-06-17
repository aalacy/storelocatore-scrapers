from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://uberall.com/api/storefinders/fh6bkacXrYxFxK28kbylc8jdborIlY/locations?v=20211005&language=de&radius=10000000&lat=51.13478252&lng=9.27347634&max=1000"
    r = session.get(api, headers=headers)
    js = r.json()["response"]["locations"]

    for j in js:
        street_address = j.get("streetAndNumber")
        city = j.get("city") or ""
        if "/" in city:
            city = city.split("/")[0].strip()
        postal = j.get("zip")
        country_code = j.get("country")
        store_number = j.get("id")
        location_name = j.get("name")
        page_url = f"https://www.star.de/service/tankstellenfinder/l/-/-/{store_number}"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = ",".join(j.get("brands") or [])

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
        hours = j.get("openingHours") or []
        for h in hours:
            index = h.get("dayOfWeek")
            day = days[index - 1]
            if h.get("closed"):
                _tmp.append(f"{day}: Closed")
                continue

            start = h.get("from1")
            end = h.get("to1")
            _tmp.append(f"{day}: {start}-{end}")

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.star.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
