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
    r = session.get("https://www.signsexpress.co.uk/centre-finder", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//div[@class="col-lg-6 centre"]/a/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.signsexpress.co.uk/"
    page_url = f"https://www.signsexpress.co.uk{url}"
    api_url = f"https://www.signsexpress.co.uk/api/pageByRoute?route={url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(api_url, headers=headers)
    j = r.json()
    a = j.get("properties")
    ad = "".join(a.get("address"))

    b = parse_address(International_Parser(), ad)
    street_address = (
        f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    postal = b.postcode or "<MISSING>"
    if postal == "<MISSING>" and ad.find(",") != -1:
        postal = ad.split(",")[-1].strip()
    country_code = "UK"
    city = b.city or "<MISSING>"
    if "Manchester" in ad:
        city = "Manchester"
    if city == "Dublin":
        country_code = "IE"
    state = a.get("region")
    location_name = j.get("name")
    phone = a.get("phone") or "<MISSING>"
    hours_of_operation = "<MISSING>"
    location_type = j.get("type")
    latitude = a.get("latitude") or "<MISSING>"
    longitude = a.get("longitude") or "<MISSING>"
    if latitude == "0":
        latitude, longitude = "<MISSING>", "<MISSING>"

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
