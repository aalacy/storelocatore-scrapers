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
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://nandos.com.my/restaurants/")
    tree = html.fromstring(r.text)

    return tree.xpath("//dl[@class='locationa-accordion']//a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='promo-pane-title']/h2/text()")
    ).strip()
    raw_address = "".join(tree.xpath("//div[@class='copy']/h5/text()"))
    street_address, city, state, postal = get_international(raw_address)
    if not city:
        city = " ".join(raw_address.split(", ")[-1].split()[:-1])
    if "1" in city:
        city = SgRecord.MISSING
    phone = "".join(tree.xpath("//div[@class='copy']/h4/text()")).strip()
    text = "".join(tree.xpath("//script[contains(text(), 'var restaurant =')]/text()"))
    try:
        latitude = text.split("{lat:")[1].split(",")[0].strip()
        longitude = text.split("lng:")[1].split("}")[0].strip()
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[contains(@class, 'timetable__day') and ./span]")
    for h in hours:
        day = "".join(h.xpath("./span[1]/text()")).strip()
        inter = "".join(h.xpath("./span[2]/text()")).strip()
        if not inter:
            continue
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)
    if "Temporarily" in location_name:
        hours_of_operation = "Temporarily Closed"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="MY",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://nandos.com.my/"
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
