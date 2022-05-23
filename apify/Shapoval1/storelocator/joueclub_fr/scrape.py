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
    r = session.get(
        "https://www.joueclub.fr/Assets/Rbs/Seo/100185/fr_FR/Rbs_Store_Store.1.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.joueclub.fr/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
    js = json.loads(js_block)
    ad = (
        "".join(js.get("address"))
        .replace("\n", " ")
        .replace("+32060345627", "")
        .strip()
    )
    a = parse_address(International_Parser(), ad)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = a.country or "<MISSING>"
    if ad.find("BELGIQUE") != -1:
        country_code = "Belgique"
    city = a.city or "<MISSING>"
    if street_address.isdigit() or street_address == "<MISSING>":
        street_address = ad.split(f"{postal}")[0].strip()
    location_name = js.get("name") or "<MISSING>"
    phone = js.get("telephone")
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="storeLocator__hoursWrapper"]//text()'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
    latitude = js.get("geo").get("latitude")
    store_number = js.get("branchCode")
    location_type = js.get("@type")
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
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
