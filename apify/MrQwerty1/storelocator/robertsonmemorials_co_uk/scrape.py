from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_regions():
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    return tree.xpath("//h3[text()='Branches']/following-sibling::ul//a/@href")


def get_urls():
    urls = []
    regions = get_regions()

    for region in regions:
        r = session.get(region)
        tree = html.fromstring(r.text)
        urls += tree.xpath(
            "//i[@class='fa fa-fw fa-phone mr-1']/preceding-sibling::a/@href"
        )

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//p[./i[@class='fa fa-fw fa-phone mr-1']]/preceding-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    postal = line.pop()
    city = line.pop()
    state = SgRecord.MISSING
    if "," in city:
        state = city.split(",")[-1].strip()
        city = city.split(",")[0].strip()
    street_address = ", ".join(line)

    country_code = "GB"
    phone = tree.xpath("//p[./i[@class='fa fa-fw fa-phone mr-1']]/text()")[0].strip()
    hours_of_operation = ";".join(tree.xpath("//h1/following-sibling::p/text()"))

    row = SgRecord(
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
    locator_domain = "https://www.robertsonmemorials.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
