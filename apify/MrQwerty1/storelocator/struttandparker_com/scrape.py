from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
    }
    r = session.get("https://www.struttandparker.com/offices", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//h1[@class='card__heading']/a/@href")


def get_data(page_url, sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": page_url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    api = f"{page_url}/map"
    if "trash/" in api:
        return
    r = session.get(api, headers=headers)
    j = r.json()["message"]["offices"][0]

    location_name = j.get("name")
    street_address = j.get("office_address")
    city = j.get("office_town")
    postal = j.get("office_postcode")
    phone = j.get("office_phone")
    latitude = j.get("office_lat")
    longitude = j.get("office_lon")
    store_number = j.get("id")

    _tmp = []
    hours = j.get("office_opening_hours") or []
    for h in hours:
        if not h.strip() or h.strip()[0] == "(":
            continue
        _tmp.append(h.strip())
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.struttandparker.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
