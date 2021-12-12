import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.lasikplus.com/sitemap-posttype-lasik_location.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))
    js = json.loads(js_block)[0]
    a = js.get("address")
    street_address = "".join(a.get("streetAddress"))
    if street_address.find("Located") != -1:
        street_address = street_address.split("Located")[0].strip()
    if street_address.find("(located") != -1:
        street_address = street_address.split("(l")[0].strip()
    if street_address.find("located") != -1:
        street_address = street_address.split("located")[0].strip()
    street_address = street_address.replace("Suite", " Suite").strip()
    street_address = " ".join(street_address.split())
    city = a.get("addressLocality")
    state = "".join(a.get("addressRegion"))
    if state.find(",") != -1:
        state = state.split(",")[0].strip()
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    location_name = js.get("name")
    phone = js.get("telephone")
    latitude = js.get("geo").get("latitude")
    longitude = js.get("geo").get("longitude")

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=SgRecord.MISSING,
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
    locator_domain = "https://www.lasikplus.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
