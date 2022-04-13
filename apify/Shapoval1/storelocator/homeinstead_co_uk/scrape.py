import json
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
    r = session.get("https://www.homeinstead.co.uk/sitemap.xml/", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "/contact-us")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.homeinstead.co.uk/"
    page_url = "".join(url)
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = tree.xpath('//p[./span[text()="Office"]]/following-sibling::p[1]/text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    if not ad:
        return
    adr = " ,".join(ad)
    js_block = "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
    js = json.loads(js_block)
    location_name = js.get("name") or "<MISSING>"
    a = parse_address(International_Parser(), adr)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    if street_address == "<MISSING>" or street_address.isdigit():
        street_address = adr.split(",")[0].strip()
    state = "".join(ad[-2]).strip()
    city = "".join(ad[-3]).strip()
    postal = "".join(ad[-1]).strip()
    country_code = "UK"
    phone = "".join(js.get("telephone")) or "<MISSING>"
    if phone.find("or") != -1:
        phone = phone.split("or")[0].strip()
    if phone.find("/") != -1:
        phone = phone.split("/")[0].strip()
    hours_of_operation = "<MISSING>"
    latitude = js.get("geo").get("latitude") or "<MISSING>"
    longitude = js.get("geo").get("longitude") or "<MISSING>"

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
        raw_address=adr,
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
