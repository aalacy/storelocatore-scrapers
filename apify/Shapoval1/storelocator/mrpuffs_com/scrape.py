from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://mrpuffs.com/wp-sitemap-posts-locations-1.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://mrpuffs.com/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = (
        "".join(tree.xpath('//i[@class="fa fa-map-marker"]/following-sibling::text()'))
        .replace("\n", "")
        .strip()
    )
    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "CA"
    city = a.city or "<MISSING>"
    location_name = (
        "".join(
            tree.xpath('//ul[@class="_listIcons mt-30"]/preceding-sibling::h3/text()')
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath('//i[@class="fa fa-phone"]/following-sibling::a/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//ul[@class="_listIcons mt-30"]/li[./i[@class="ion-ios-calendar"]][1]//text()'
            )
        )
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
        latitude=SgRecord.MISSING,
        longitude=SgRecord.MISSING,
        hours_of_operation=hours_of_operation,
        raw_address=ad,
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
