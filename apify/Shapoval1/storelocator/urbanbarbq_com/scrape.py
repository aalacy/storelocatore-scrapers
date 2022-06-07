from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    r = session.get("https://www.urbanbarbq.com/Locations.aspx")
    tree = html.fromstring(r.text)
    return tree.xpath('//a[@class="lnkStoreName"]/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://urbanbarbq.com/"
    page_url = f"https://www.urbanbarbq.com{url}"
    r = session.get(page_url)

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath('//div[@class="store-name"]/span/text()'))
    blink = "<MISSING>"
    if location_name.find("BWI Airport") != -1:
        blink = "".join(tree.xpath('//span[@class="blinkMe"]/text()')).strip()
    hours_of_operation = "<MISSING>"
    if blink != "<MISSING>":
        hours_of_operation = blink
    if hours_of_operation == "":
        hours_of_operation = "<MISSING>"
    country_code = "US"
    line = "".join(tree.xpath('//div[@class="store-address-line2"]/text()')).replace(
        "-", " "
    )
    street_address = "".join(tree.xpath('//div[@class="store-address-line1"]/text()'))
    postal = line.split()[2]
    city = line.split()[0]
    state = line.split()[1]
    phone = "".join(tree.xpath('//span[@class="store-phone"]/text()'))

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
        latitude=SgRecord.MISSING,
        longitude=SgRecord.MISSING,
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
