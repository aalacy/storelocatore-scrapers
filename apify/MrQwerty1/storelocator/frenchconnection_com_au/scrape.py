import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.frenchconnection.com.au/on/demandware.store/Sites-frenchconnection-au-Site/en_AU/AllStores",
        headers=headers,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//p[@class='store-name']/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    store_number = page_url.split("=")[-1]
    location_name = "".join(tree.xpath("//h1[@class='hidden-phone']/text()")).strip()
    street_address = (
        "".join(tree.xpath("//span[@class='street-address2']/text()")).strip()
        or "".join(tree.xpath("//span[@class='street-address1']/text()")).strip()
    )
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    phone = "".join(tree.xpath("//span[@itemprop='telephone']/a/text()")).strip()

    text = "".join(tree.xpath("//script[contains(text(), 'var storeModel =')]/text()"))
    text = text.split("var storeModel =")[1].split("};")[0] + "}"
    j = json.loads(text)
    location_type = j.get("StoreType")
    latitude = j.get("Latitude") or ""
    longitude = j.get("Longitude") or ""
    if str(latitude) == "0":
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[contains(@class, 'store-detail')]//table//tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        inter = "".join(h.xpath("./td[2]//text()")).strip()
        if inter:
            _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="AU",
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        phone=phone,
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
    locator_domain = "https://www.frenchconnection.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.frenchconnection.com.au/on/demandware.store/Sites-frenchconnection-au-Site/en_AU/AllStores",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
