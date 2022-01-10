import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    api_url = "https://charge.pod-point.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var podAddresses =")]/text()'))
        .split("var podAddresses =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    tmp = []
    for j in js:
        ids = j.get("id")
        tmp.append(ids)
    return tmp


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        opens = h.get("from")
        closes = h.get("to")
        line = f"{day} {opens} - {closes}".replace(":00:00", ":00").strip()
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def get_data(url, sgw: SgWriter):
    locator_domain = "https://pod-point.com/"
    api_url = f"https://charge.pod-point.com/ajax/pods/{url}"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(api_url, headers=headers)
    try:
        j = r.json()
    except:
        return
    a = j.get("address")
    aa = a.get("address")
    store_number = a.get("id")
    location_name = a.get("name")
    street_address = f"{aa.get('address1')} {aa.get('address2')}".strip()
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    postal = aa.get("postcode")
    country_code = aa.get("country")
    city = aa.get("town")
    slug = a.get("slug")
    page_url = f"https://charge.pod-point.com/address/{slug}"
    latitude = a.get("latitude")
    longitude = a.get("longitude")
    location_type = a.get("type")
    hours_of_operation = "<MISSING>"
    hours = a.get("opening").get("times") or "<MISSING>"
    if hours != "<MISSING>":
        hours_of_operation = get_hours(hours)

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=SgRecord.MISSING,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
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
