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
    r = session.get("https://www.fressnapf.de/sitemap-store.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.fressnapf.de/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    try:
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
    except:
        return
    js_block = "".join(tree.xpath('//script[@type="application/ld+json"]//text()'))
    js = json.loads(js_block)[1]
    location_name = js.get("name") or "<MISSING>"
    location_type = js.get("@type") or "<MISSING>"
    a = js.get("address")
    if not a:
        return
    street_address = a.get("streetAddress") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    latitude = js.get("geo").get("latitude") or "<MISSING>"
    longitude = js.get("geo").get("longitude") or "<MISSING>"
    phone = js.get("telephone") or "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="sot-weekdays"]/div//text()'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
    if hours_of_operation.find("15.08.22") != -1:
        hours_of_operation = hours_of_operation.split("15.08.22")[0].strip()

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
        location_type=location_type,
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
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
