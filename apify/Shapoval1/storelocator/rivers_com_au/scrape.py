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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.rivers.com.au/store/StoreDirectory", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[contains(@href, "stores")]/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.rivers.com.au/"
    page_url = f"https://www.rivers.com.au{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ad = tree.xpath('//h4[text()="Address"]/following-sibling::p[1]/text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    js_block = "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))

    street_address = (
        js_block.split('"streetAddress": "')[1]
        .split('"')[0]
        .replace("&amp;", "&")
        .replace(",", "")
        .strip()
    )
    city = js_block.split('"addressLocality": "')[1].split('"')[0].strip()
    state = js_block.split('"addressRegion": "')[1].split('"')[0].strip()
    postal = "".join(ad[-1]).strip()
    country_code = "AU"
    location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
    phone = (
        "".join(tree.xpath('//span[contains(text(), "Phone")]/text()'))
        .replace("Phone:", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath('//h4[text()="Opening Hours"]/following-sibling::*[1]//text()')
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    latitude = js_block.split('"latitude": "')[1].split('"')[0].strip()
    longitude = js_block.split('"longitude": "')[1].split('"')[0].strip()
    if latitude == longitude:
        latitude, longitude = "<MISSING>", "<MISSING>"

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
        raw_address=" ".join(ad).strip(),
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
