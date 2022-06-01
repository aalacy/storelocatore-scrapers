import json
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
    r = session.get(
        "https://www.ah.nl/sitemaps/entities/stores/stores.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.ah.nl/"
    page_url = "".join(url)
    if page_url.count("/") != 7:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
    js = json.loads(js_block)
    a = js.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "NL"
    location_name = "".join(js.get("name")) or "<MISSING>"
    phone = js.get("telephone") or "<MISSING>"
    hours_of_operation = "<MISSING>"
    hours = js.get("openingHoursSpecification")
    tmp = []
    if hours:
        for h in hours:
            day = h.get("dayOfWeek")
            opens = h.get("opens")
            closes = h.get("closes")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)
    page_url = js.get("url")
    latitude = js.get("geo").get("latitude")
    longitude = js.get("geo").get("longitude")
    store_number = "<MISSING>"
    try:
        location_type = (
            "".join(tree.xpath('//script[contains(text(), "storeType")]/text()'))
            .split('"storeType":"')[1]
            .split('"')[0]
            .strip()
        )
    except:
        location_type = "<MISSING>"
    slug = str(page_url).split("/")[-1].strip()
    if slug.isdigit():
        store_number = slug
    if location_type == "REGULAR":
        location_name = "Ah"
    if location_type == "TOGO":
        location_name = "AH To Go"
    if location_type == "XL":
        location_name = "AH XL"

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
