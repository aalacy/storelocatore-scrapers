from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_ids():
    _ids = []
    r = session.get(
        "https://nossaslojas.americanas.com.br/static/json/lojas_mapahome.json",
        headers=headers,
    )
    js = r.json()

    for j in js:
        _ids.append(j["Loja"])

    return _ids


def get_phones():
    phone = dict()
    r = session.get(
        "https://nossaslojas.americanas.com.br/static/json/lojas_wpp.json",
        headers=headers,
    )
    js = r.json()["Ativas"]

    for j in js:
        _id = j.get("Loja")
        text = j.get("Link") or ""
        try:
            p = text.split("phone=")[1].split("&")[0]
        except:
            p = SgRecord.MISSING
        phone[_id] = p

    return phone


def get_data(store_number, sgw: SgWriter):
    api = f"https://restql-api-v2-itg.b2w.io/acom/run-query/yourdev/store-details/2?sellerStoreId={store_number}"
    page_url = f"https://nossaslojas.americanas.com.br/loja/{store_number}"

    r = session.get(api, headers=headers)
    logger.info(f"{api}: {r.status_code}")
    js = r.json()["store-v2-capacity"]["result"]["stores"]

    for j in js:
        location_name = j.get("name")
        a = j.get("address")
        street_address = a.get("address")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        country_code = "BR"
        phone = phones.get(store_number)

        g = j.get("geolocation")
        latitude = g.get("latitude")
        longitude = g.get("longitude")

        _tmp = []
        hours = j.get("schedules") or {}
        for day, v in hours.items():
            start = v.get("start")
            end = v.get("end")
            if not start:
                _tmp.append(f"{day}: Closed")
                continue
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    locator_domain = "https://americanas.com.br"
    logger = sglog.SgLogSetup().get_logger(logger_name="americanas.com.br")
    phones = get_phones()
    ids = get_ids()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
