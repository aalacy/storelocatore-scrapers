from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.tastee-freez.com/locations-all/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://www.tastee-freez.com/locations-all/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[@class="storelocatorlink"]/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.tastee-freez.com"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.tastee-freez.com/locations-all/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
    city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
    state = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
    postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
    country_code = "US"
    location_name = " ".join(
        tree.xpath('//h1[@class="page-header-title"]/text()')
    ).split(",")[0]
    phone = "".join(tree.xpath('//a[@class="call"]/text()'))
    text = "".join(tree.xpath('//img[contains(@src, "maps")]/@src'))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if text:
        latitude = text.split("location=")[1].split(",")[0].strip()
        longitude = text.split(",")[-1].strip()
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="location-hours"]//text()'))
        .replace("\n", "")
        .replace("  -  ", " - ")
        .strip()
    )

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
        raw_address=f"{street_address} {city}, {state} {postal}",
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):

    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
