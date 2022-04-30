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
    r = session.get("https://palmbeachtan.com/sitemap-locations.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://palmbeachtan.com/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//*[@itemprop="streetAddress"]/text()')) or "<MISSING>"
    )
    city = "".join(tree.xpath('//*[@itemprop="addressLocality"]/text()')) or "<MISSING>"
    state = "".join(tree.xpath('//*[@itemprop="addressRegion"]/text()')) or "<MISSING>"
    postal = "".join(tree.xpath('//*[@itemprop="postalCode"]/text()')) or "<MISSING>"
    country_code = "US"
    location_name = (
        "".join(
            tree.xpath('//div[@class="location-info"]/preceding-sibling::h1/text()')
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    phone = "".join(tree.xpath('//*[@itemprop="telephone"]/text()')) or "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath('//h3[text()="Hours:"]/following-sibling::div[1]/div//text()')
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "".join(tree.xpath("//*/@data-lat"))
    longitude = "".join(tree.xpath("//*/@data-lng"))

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
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
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
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
