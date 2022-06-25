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
    r = session.get("https://boutique.sfr.fr/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://sfr.fr/"
    page_url = url
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//meta[@itemprop="streetAddress"]/@content')) or "<MISSING>"
    )
    if street_address == "<MISSING>":
        return
    city = "".join(tree.xpath('//meta[@itemprop="addressLocality"]/@content'))
    country_code = "FR"
    location_name = " ".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
    phone = (
        "".join(tree.xpath('//div[@itemprop="telephone"]//text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath('//meta[@itemprop="latitude"]/@content'))
    longitude = "".join(tree.xpath('//meta[@itemprop="longitude"]/@content'))
    hours_of_operation = (
        " ".join(
            tree.xpath('//table[@class="c-location-hours-details"]//tr//td//text()')
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"
    postal = (
        "".join(
            tree.xpath(
                '//div[@class="NAP"]//span[@class="c-address-postal-code"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath('//ol[@class="c-bread-crumbs-list"]/li[2]//text()'))
        or "<MISSING>"
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
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
