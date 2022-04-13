from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.topsmarkets.com/StoreLocator/Search/?ZipCode=10001&miles=5000"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@id='StoreLocator']//tr[not(@class)]/td/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    store_number = "".join(tree.xpath("//p[@class='StoreNumber']/text()")).strip()
    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    csz = line.pop()
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state, postal = csz.split()
    street_address = ", ".join(line)

    text = "".join(tree.xpath("//script[contains(text(), 'initializeMap')]/text()"))
    try:
        latitude, longitude = eval(text.split("initializeMap")[1].split(";")[0])
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    try:
        phone = tree.xpath("//p[@class='PhoneNumber']/a/text()")[-1].strip()
    except IndexError:
        phone = SgRecord.MISSING

    location_name = "".join(tree.xpath("//h3/text()")).strip() or city
    hours_of_operation = ";".join(
        tree.xpath("//dt[contains(text(), 'Pharmacy')]/following-sibling::dd/text()")
    ).strip()
    if not hours_of_operation:
        return

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "https://www.topsmarkets.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
