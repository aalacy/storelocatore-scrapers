import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_data(_id, sgw: SgWriter):
    data = json.dumps({"city_id": _id})
    try:
        r = session.post(
            "https://www.vodafone.ua/shops", data=data, headers=headers, cookies=cookies
        )
        jso = r.json()
    except:
        return

    js = jso["data"]
    c = jso["city"]
    city = c.get("label")
    page_url = c.get("url")

    for j in js:
        location_name = j.get("name")
        street_address = location_name
        p = j.get("position") or {}
        latitude = p.get("lat")
        longitude = p.get("lng")
        if latitude == 0:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = j.get("work_hours") or ""
        hours_of_operation = " ".join(hours_of_operation.replace("<br>", ";").split())
        if "Згідно" in hours_of_operation:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="UA",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = [str(i) for i in range(1, 400)]

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.ua/"
    session = SgRequests()
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-CSRF-TOKEN": "l9ADbj6Ye1ly3vIzerkcgBS8VsmL1gzUnNB88xMc",
    }
    cookies = {
        "www_vodafone_ua_session": "eyJpdiI6InU5MlRYY1hBRWJKbXd6VUQ2dTV6ekE9PSIsInZhbHVlIjoiWkJnZUwwOTZkdU1aUGlpS1BYUmhJSEsrc0ZUaU96ZUhnQkdGVUhNQjFEUmpKNk5aSUlYcW13ejJwalZTdjFZcENpWXArSVRNS21DVzYyc0JCZ0xkcGJNdlRIbFdnaG1LelV6WmZSb1hwMGdhaWh6M2ZCR0g2K3MrUjR1M2hpbUsiLCJtYWMiOiJjMWJmMDA5NjAxMmMxMzZiNTAxZDc2YTQ0YmJmNTEzNTM0YzYyNWNmM2RhMzA0MzRkYWZmNWQ5NzczODRmZmNkIn0%3D",
    }
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.CITY})
        )
    ) as writer:
        fetch_data(writer)
