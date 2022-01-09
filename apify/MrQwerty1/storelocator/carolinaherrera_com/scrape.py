from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get(
        "https://carolinaherreraboutiques.com/api/stores?lat=40.7127753&lng=-74.0059728"
    )
    amount = r.json()["data"]["pager"]["total_pages"] + 1

    for page_num in range(1, amount):
        urls.append(
            f"https://carolinaherreraboutiques.com/api/stores?lat=40.7127753&lng=-74.0059728&page={page_num}"
        )

    return urls


def get_data(api, sgw: SgWriter):
    r = session.get(api)
    js = r.json()["data"]["rows"]

    for j in js:
        location_name = j.get("store_name")
        phone = j.get("phone_number")
        if phone == "NULL":
            phone = "<MISSING>"
        street_address = f"{j.get('address_1')} {j.get('address_2') or ''}".strip()
        city = j.get("city")
        city = city.replace("&#039;", "'")
        state = j.get("state") or SgRecord.MISSING
        postal = j.get("postal_code")
        if state == "Florida" and "FL" in postal:
            postal = postal.replace("FL", "").strip()
        country_code = j.get("country_code") or SgRecord.MISSING

        if country_code == SgRecord.MISSING and state != SgRecord.MISSING:
            country_code = state
            state = SgRecord.MISSING

        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("store_number")
        location_type = j.get("store_type")
        page_url = f"https://store-locator.carolinaherrera.com/en/{j.get('slug')}"

        _tmp = []
        hours = j.get("store_timings") or []

        for h in hours:
            start_day = h.get("start_day")
            end_day = h.get("end_day")
            from_time = h.get("from_time")
            to_time = h.get("to_time")
            if start_day == end_day:
                if from_time and from_time != to_time:
                    _tmp.append(f"{start_day}: {from_time} - {to_time}")
                else:
                    _tmp.append(f"{start_day}: Closed")
            else:
                if from_time and from_time != to_time:
                    _tmp.append(f"{start_day}-{end_day}: {from_time} - {to_time}")
                else:
                    _tmp.append(f"{start_day}-{end_day}: Closed")

            if start_day == "Sun" and end_day == "Sat":
                break

        hours_of_operation = ";".join(_tmp) or SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://carolinaherreraboutiques.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
