import typing
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.blazingonion.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@href, '/locations')]/following-sibling::ul//a/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h3[contains(@id, 'ctl01_rptAddresses_ctl00_lblCaption')]/text()")
    ).strip()
    street_address = "".join(
        tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pAddressInfo']/text()")
    ).strip()

    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = "".join(
        tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pStateZip']/text()")
    ).strip()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = (
        "".join(tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pPhonenum']/text()"))
        .replace("Phone", "")
        .replace(".", "")
        .strip()
    )

    _tmp = []  # type: typing.List[str]
    hours = tree.xpath("//div[@id='ctl01_pSpanDesc']//text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    rec = False
    for h in hours:
        if ("Sports Lounge:" in h or "Whiskey" in h or "Mall" in h) and _tmp:
            break
        if "Sports Lounge" in h:
            rec = False
        if rec:
            _tmp.append(h.replace(",", ""))
        if (
            h == "Restaurant and Lounge Hours:"
            or h == "Restaurant Hours:"
            or h == "Restaurant:"
            or h == "estaurant Hours:"
        ):
            rec = True

    hours_of_operation = " ".join(_tmp).strip().replace("pm ", "pm;")
    if "We" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("We")[0]
    if "There's" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("There's")[0]
    if hours_of_operation.endswith(";"):
        hours_of_operation = hours_of_operation[:-1]

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

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.blazingonion.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
