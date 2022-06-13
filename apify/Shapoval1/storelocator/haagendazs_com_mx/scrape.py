import urllib.parse
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
    r = session.get("https://www.haagendazs.com.mx/shop/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.anthonys.com"
    page_url = "".join(url)
    if page_url.count("/") != 5:
        return
    slug = urllib.parse.quote(page_url).replace("%3A", ":")
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(slug, headers=headers)

    tree = html.fromstring(r.text)

    location_name = (
        " ".join(tree.xpath('//span[@itemprop="name"]/span/text()'))
        .replace("\n", "")
        .strip()
    )
    street_address = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//span[@class="c-address-street-1"]/text()'
            )
        )
        + " "
        + "".join(
            tree.xpath(
                '//div[@class="Core-address"]//span[@class="c-address-street-2"]/text()'
            )
        )
    )
    state = "".join(
        tree.xpath(
            '//div[@class="Core-address"]//span[@class="c-address-state"]/text()'
        )
    )
    postal = "".join(
        tree.xpath(
            '//div[@class="Core-address"]//span[@class="c-address-postal-code"]/text()'
        )
    )
    country_code = "MX"
    city = "".join(
        tree.xpath('//div[@class="Core-address"]//span[@class="c-address-city"]/text()')
    )
    latitude = "".join(
        tree.xpath('//div[@class="Core-address"]//meta[@itemprop="latitude"]/@content')
    )
    longitude = "".join(
        tree.xpath('//div[@class="Core-address"]//meta[@itemprop="longitude"]/@content')
    )
    phone = "".join(tree.xpath('//div[@itemprop="telephone"]/text()')) or "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath('//table[@class="c-hours-details"]//tr/td//text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())

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
