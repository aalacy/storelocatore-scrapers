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
    r = session.get("https://www.paul-uk.com/find-a-paul")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'More info')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = " ".join(
        ", ".join(tree.xpath("//div[@class='shop-info']/p[1]/text()")).split()
    )
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(tree.xpath("//div[@class='shop-info']/p[2]/text()")).strip()
    try:
        text = "".join(tree.xpath("//script[contains(text(), 'storeList')]/text()"))
        latitude = text.split('lat":"')[1].split('"')[0]
        longitude = text.split('lng":"')[1].split('"')[0]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//div[@class='shop-name']/following-sibling::div/p[not(@class)]/text()"
    )
    for h in hours:
        if not h.strip():
            continue

        _tmp.append(h)
        if "Sunday" in h:
            break

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
