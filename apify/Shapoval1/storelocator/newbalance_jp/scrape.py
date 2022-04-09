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
    r = session.get("https://company.newbalance.jp/store-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'store/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://newbalance.jp/"
    page_url = "".join(url)
    if page_url.find("concept-store") != -1:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    slug = "".join(tree.xpath('//div[@class="store_meta"]/p[1]/text()'))
    location_name = "<MISSING>"
    if slug == "Factory store":
        location_name = "New Balance Factory Store"
    if slug == "Official Store":
        location_name = "New Balance Official Store"
    ad = "".join(tree.xpath('//p[@class="store_address"]/text()'))

    a = parse_address(International_Parser(), ad)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "JP"
    city = a.city or "<MISSING>"
    phone = (
        "".join(tree.xpath('//h3[text()="電話番号"]/following-sibling::p[1]/text()'))
        or "<MISSING>"
    )
    if phone.find("※") != -1:
        phone = phone.split("※")[0].strip()
    hours_of_operation = (
        "".join(tree.xpath('//h3[text()="営業時間"]/following-sibling::p[1]/text()'))
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div/@data-lat"))
    longitude = "".join(tree.xpath("//div/@data-lng"))
    if hours_of_operation.find("（") != -1:
        hours_of_operation = hours_of_operation.split("（")[0].strip()

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
