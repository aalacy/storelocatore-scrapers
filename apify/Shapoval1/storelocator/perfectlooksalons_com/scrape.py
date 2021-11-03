from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_data_req():
    api_url = "https://perfectlooksalons.bookedby.com/api/v1/Stores/Map"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json;charset=utf-8",
        "X-BookedBy-Context": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhOTU1NTMzYy1lMjE0LTRiOWUtYjhiNC02YzVlYzViNmMwNjIiLCJCb29raW5nR3JvdXBJZCI6ImRiOGY1ZjhjLTA1ZDUtNDRkZC1iMjA3LTUwNmUxODc3ZTY4YSIsIkJvb2tpbmdHcm91cFR5cGUiOiIxIiwiQm9va2luZ0dyb3VwT3BlcmF0aW9uTW9kZSI6IjIiLCJleHAiOjE2NjA3NTczMDksImlzcyI6ImJvb2tlZGJ5LmNvbSIsImF1ZCI6ImJvb2tlZGJ5LmNvbSJ9.1UdYViCJyTTUmGw7g7e_mmVIOaew_wqAhbWORzX5Bow",
        "Request-Id": "|RZuR4.Cq+Ub",
        "Origin": "https://perfectlooksalons.bookedby.com",
        "Connection": "keep-alive",
        "Referer": "https://perfectlooksalons.bookedby.com/search-map?bbox@:-196.78025&:-10.674501&:12.544942&:67.122256",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = '{"mapAreaList":[{"associativeUid":"f47ab5b3-1906-48ae-9add-eae695700b47","mapArea":{"centerLat":28.223877499999993,"centerLon":-92.11765399999999,"width":209.325192,"height":77.79675699999999}},{"associativeUid":"3034958c-fd33-48a5-8a7c-fb59bb327344","mapArea":{"centerLat":61.395,"centerLon":-153.885,"width":59.230000000000004,"height":20.570000000000007}},{"associativeUid":"a97793e0-2eab-4777-866e-7b35c4e25311","mapArea":{"centerLat":20.725,"centerLon":-157.33,"width":7,"height":4.970000000000002}}],"services":[]}'
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["response"][0]["storePins"]
    storeUids = []
    for j in js:
        storeUid = j.get("storeUid")
        storeUids.append(storeUid)
    return storeUids


def get_hours(hours) -> str:

    tmp = []
    for h in hours:
        day = h.get("weekday")
        open = h.get("regularSchedule").get("fromTime1")
        close = h.get("regularSchedule").get("toTime1")
        line = f"{day} {open} - {close}"
        tmp.append(line)
    hours_of_operation = (
        "; ".join(tmp)
        .replace("1 ", "Monday ")
        .replace("2 ", "Tuesday ")
        .replace("3 ", "Wednesday ")
        .replace("4 ", "Thursday ")
        .replace("5 ", "Friday ")
        .replace("6 ", "Saturday ")
        .replace("7 ", "Sunday ")
        or "<MISSING>"
    )
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://perfectlooksalons.com/"
    api_url = "https://perfectlooksalons.bookedby.com/api/v1/Stores/List"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json;charset=utf-8",
        "X-BookedBy-Context": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhOTU1NTMzYy1lMjE0LTRiOWUtYjhiNC02YzVlYzViNmMwNjIiLCJCb29raW5nR3JvdXBJZCI6ImRiOGY1ZjhjLTA1ZDUtNDRkZC1iMjA3LTUwNmUxODc3ZTY4YSIsIkJvb2tpbmdHcm91cFR5cGUiOiIxIiwiQm9va2luZ0dyb3VwT3BlcmF0aW9uTW9kZSI6IjIiLCJleHAiOjE2NjA3NTczMDksImlzcyI6ImJvb2tlZGJ5LmNvbSIsImF1ZCI6ImJvb2tlZGJ5LmNvbSJ9.1UdYViCJyTTUmGw7g7e_mmVIOaew_wqAhbWORzX5Bow",
        "Request-Id": "|RZuR4.j+Rmj",
        "Request-Context": "appId=cid-v1:52c40e8e-9455-4104-a846-cbc1b531a956",
        "Origin": "https://perfectlooksalons.bookedby.com",
        "Connection": "keep-alive",
        "Referer": "https://perfectlooksalons.bookedby.com/search-map?bbox@:-117.642727&:42.439372&:-111.399363&:43.778571",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    stores = get_data_req()
    for s in stores:

        data = '["' + s + '"]'
        r = session.post(api_url, headers=headers, data=data)
        js = r.json()["response"]
        for j in js:
            slug = j.get("uid")
            a = j.get("address")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            location_name = j.get("name")

            page_url = f"https://perfectlooksalons.bookedby.com/store/{slug}"
            street_address = f"{a.get('street1')} {a.get('street2') or ''}".strip()
            if (
                page_url
                == "https://perfectlooksalons.bookedby.com/store/19570ee8-908a-448e-99a0-5c9c8459319d"
            ):
                street_address = "<MISSING>"
                location_name = "125 - Moses Lake"
            state = a.get("state") or "<MISSING>"
            postal = a.get("zip") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            if (
                city.find("Tumwater - Salon 117") != -1
                or city.find("Longview - Salon 074") != -1
            ):
                city = city.split("-")[0].strip()
            if (
                city.find("116 - Lebanon") != -1
                or city.find("Salon 126 - Roseburg") != -1
            ):
                city = city.split("-")[1].strip()
            phone = j.get("phone") or "<MISSING>"
            hours = j.get("weeklySchedules")
            hours_of_operation = get_hours(hours)

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
