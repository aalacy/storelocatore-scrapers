from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    tmp = []
    for i in range(1, 1500):
        tmp.append(i)
    return tmp


def get_data(url, sgw: SgWriter):
    locator_domain = "https://5ka.ru/"
    api_url = f"https://5ka.ru/api/v3/stores/?lat=55.75322&lon=37.622513&page={url}&radius=1000000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(api_url, headers=headers)

    js = r.json()["results"]
    for j in js:

        page_url = "https://5ka.ru/stores/"
        location_type = j.get("type") or "<MISSING>"
        street_address = "".join(j.get("address")) or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        country_code = "RU"
        city = j.get("city_name") or "<MISSING>"
        if street_address.find(f"{city}") != -1:
            street_address = (
                street_address.replace(f"{city}", "").replace(",", "").strip()
            )
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            f"{j.get('work_start_time')} - {j.get('work_end_time')}" or "<MISSING>"
        )
        hours_of_operation = hours_of_operation.replace(
            "None - None", "<MISSING>"
        ).strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
