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
        "https://www.homeinstead.com/contentassets/c7e231f6da7542eea92cd193a735f2b6/sitemap.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "/location/")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.homeinstead.com/"
    page_url = "".join(url)
    if page_url == "https://www.homeinstead.com/location/":
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//main[@id="page-content"]/script[1]/text()'))
    js = json.loads(js_block)
    a = js.get("address")
    location_name = js.get("name") or "<MISSING>"
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    if str(postal).find(" ") != -1:
        country_code = "CA"
    if city == "London":
        country_code = "UK"
    phone = js.get("telephone") or "<MISSING>"
    latitude = js.get("geo").get("latitude")
    longitude = js.get("geo").get("longitude")
    store_number = page_url.split("/")[-2].strip()
    days = " ".join(js.get("openingHoursSpecification").get("dayOfWeek"))
    if days == "Sunday Monday Tuesday Wednesday Thursday Friday Saturday":
        days = "Sunday - Saturday:"
    opens = js.get("openingHoursSpecification").get("opens")
    closes = js.get("openingHoursSpecification").get("closes")
    hours_of_operation = f"{days} {opens} - {closes}"

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
