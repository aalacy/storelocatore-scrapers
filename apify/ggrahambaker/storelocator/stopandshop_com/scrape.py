from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://stores.stopandshop.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://stopandshop.com/"
    page_url = "".join(url)
    if page_url.count("/") != 5:
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    street_address = (
        "".join(tree.xpath('//h1//meta[@itemprop="streetAddress"]/@content'))
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath('//h1//span[@class="c-address-city"]/text()')) or "<MISSING>"
    )
    state = (
        "".join(tree.xpath('//h1//abbr[@class="c-address-state"]/text()'))
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('//h1//span[@class="c-address-postal-code"]/text()'))
        or "<MISSING>"
    )
    country_code = "US"
    location_name = (
        "".join(tree.xpath('//meta[@itemprop="name"]/@content')) or "<MISSING>"
    )
    phone = (
        "".join(
            tree.xpath(
                '//h1/following-sibling::div[1]//span[@itemprop="telephone"]/text()'
            )
        ).strip()
        or "<MISSING>"
    )
    store_number = (
        "".join(tree.xpath('//div[@class="StoreDetails-storeNum"]/text()'))
        .replace("\n", "")
        .replace("#", "")
        .strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath('//h1//meta[@itemprop="latitude"]/@content')) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath('//h1//meta[@itemprop="longitude"]/@content')) or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="c-location-hours"]//tr/@content'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    per_clos = "".join(
        tree.xpath(
            '//div[contains(text(), "CLOSED")]/text() | //div[contains(text(), "STORE HAS BEEN RELOCATED TO")]/text()'
        )
    )
    if per_clos:
        return

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
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
