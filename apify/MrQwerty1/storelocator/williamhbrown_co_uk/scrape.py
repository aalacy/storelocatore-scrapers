import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.williamhbrown.co.uk/branch-list")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='list-group-item wide' and contains(@href, '/estate-agents/')]/@href"
    ), tree.xpath(
        "//a[@class='list-group-item wide' and contains(@href, '/estate-agents-in-')]/@href"
    )


def get_multiple(slug):
    urls = []
    r = session.get(f"https://www.williamhbrown.co.uk{slug}")
    if r.status_code == 404:
        return []
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var branches')]/text()"))
    try:
        text = text.split("var branches =")[1].split("}]}];")[0] + "}]}]"
    except IndexError:
        return []
    js = json.loads(text)
    for j in js:
        urls.append(j.get("Url"))

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.williamhbrown.co.uk{slug}"
    r = session.get(page_url)
    try:
        tree = html.fromstring(r.text)
    except:
        return

    location_name = "".join(tree.xpath("//h1/span[1]/text()")).strip()
    raw_address = " ".join(" ".join(tree.xpath("//address/text()")).split())
    street_address, city, state, postal = get_international(raw_address)
    try:
        phone = tree.xpath("//a[contains(@href, 'tel:')]/@href")[0].replace("tel:", "")
    except IndexError:
        phone = SgRecord.MISSING

    text = "".join(tree.xpath("//script[contains(text(), 'maps.LatLng(')]/text()"))
    try:
        latitude = text.split("maps.LatLng(")[1].split(",")[0]
        longitude = text.split("maps.LatLng(")[1].split(",")[1].replace(")", "")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//div[@class='opening-times-header']/following-sibling::div/span"
    )
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls, multi = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_multiple, url): url for url in multi}
        for future in futures.as_completed(future_to_url):
            if future.result():
                urls += future.result()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.williamhbrown.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
