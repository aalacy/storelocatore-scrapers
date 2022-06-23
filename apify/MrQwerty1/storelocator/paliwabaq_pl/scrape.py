import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    ids = set()
    r = session.get(
        "https://www.paliwabaq.pl/_layouts/f2hPaliwaBaq/default.aspx?language=cs",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@id='JsonResult']/text()"))
    js = json.loads(text)

    for j in js:
        ids.add(j.get("id"))

    return ids


def get_data(store_number, sgw: SgWriter):
    page_url = f"https://www.paliwabaq.pl/_layouts/f2hPaliwaBaq/detail.aspx?includeRawFields=1&ID={store_number}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//div[@id='JsonResult']/text()"))
    j = json.loads(text)[0]

    location_name = f'Stacja - {j.get("value")}'
    street_address = j.get("ulice")
    city = j.get("mesto")
    postal = j.get("psc")
    country_code = "PL"
    phone = j.get("telefon") or ""
    latitude = j.get("lat")
    longitude = j.get("lng")
    hours_of_operation = j.get("open_hours") or ""

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone.replace("x", ""),
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation.replace("x", ""),
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.paliwabaq.pl"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
