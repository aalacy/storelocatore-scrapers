from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://westvillenyc.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='btn-sketch text-white']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//p[@class='mb-1 single-location-txt']/text()")
    street_address = line.pop(0).strip()
    phone = line.pop(1)
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state = csz.split()[0]
    postal = csz.split()[1]

    _tmp = []
    hours = tree.xpath("//p[contains(text(), 'Hours')]/text()")
    for h in hours:
        if not h.strip() or "PLEASE" in h or "LOCATION" in h or "Hours" in h:
            continue
        _tmp.append(h.strip())

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
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
    locator_domain = "https://westvillenyc.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
