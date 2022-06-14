import gzip
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures

session = SgRequests()


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://www.exxon.com/en/-/media/files/wep/sitemapxml/exxon-retail-us/sitemap0.gz?sc_lang=en&hash=3CC8B3E5ADBAB221276FF3BFBB3CC3D3",
        headers=headers,
    )
    tree = html.fromstring(gzip.decompress(r.content))
    return tree.xpath('//loc[contains(text(), "en/find-station/")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.exxon.com/"
    page_url = url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[contains(text(), "streetAddress")]/text()'))
    js = json.loads(js_block)
    a = js.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    if str(street_address).endswith(",") != -1:
        street_address = "".join(street_address[:-1]).strip()
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressCountry") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    location_name = js.get("name") or "<MISSING>"
    phone = js.get("telephone") or "<MISSING>"
    latitude = js.get("geo").get("latitude") or "<MISSING>"
    longitude = js.get("geo").get("longitude") or "<MISSING>"
    try:
        store_number = str(page_url).split("-")[-1].strip()
    except:
        store_number = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3[text()="Location hours"]/following-sibling::ul//li//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
    location_type = "<MISSING>"
    loc_img = js.get("image")
    if "/exxon-sm" in str(loc_img):
        location_type = "exxon"
    if "/mobil-sm" in str(loc_img):
        location_type = "mobil"

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
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
