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
    r = session.get("https://www.speedyservices.com/depot/a-z", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath('//div[@class="result-depot"]/a/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.speedyservices.com/"
    page_url = f"https://www.speedyservices.com{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = (
        " ".join(tree.xpath('//div[@id="Address"]/p[1]//text()'))
        .replace("\n", "")
        .strip()
    )
    ad = " ".join(ad.split())
    a = parse_address(International_Parser(), ad)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "")
        .replace("Speedy @ B&Q", "")
        .replace("Speedy & B&Q", "")
        .strip()
    )
    if ad.find("Unit C/D") != -1:
        street_address = " ".join(ad.split(",")[:3]).strip()
        street_address = " ".join(street_address.split())
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "UK"
    city = a.city or "<MISSING>"
    location_name = "".join(tree.xpath('//h1[@class="location-results-name"]/text()'))
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("LatLng(")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("LatLng(")[1]
        .split(",")[1]
        .split(")")[0]
        .strip()
    )
    phone = (
        "".join(tree.xpath('//div[@id="Address"]//a[contains(@href, "tel")]/text()'))
        or "<MISSING>"
    )
    if phone.find("E") != -1:
        phone = phone.split("E")[0].strip()
    hours_of_operation = (
        " ".join(tree.xpath('//div[@id="working-hours"]/div//text()'))
        .replace("\n", "")
        .strip()
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
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
