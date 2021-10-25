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
    r = session.get("https://ultimartstores.com/our-locations/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//h4/a/@href")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://ultimartstores.com/"
    page_url = url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    street_address = (
        "".join(
            tree.xpath(
                '//div[@class="listing-main-content"]//h2/following-sibling::p[1]/strong[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(
            tree.xpath(
                '//div[@class="listing-main-content"]//h2/following-sibling::p[1]/strong[2]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    location_name = (
        "".join(tree.xpath('//div[@class="listing-main-content"]//h2/text()'))
        or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath('//strong[text()="Phone:"]/following-sibling::text()[1]'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = (
        "".join(tree.xpath('//strong[text()="Hours:"]/following-sibling::text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div/@data-latitude")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div/@data-longitude")) or "<MISSING>"

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
        raw_address=street_address + " " + ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
