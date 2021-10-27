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


def get_children(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@style='background-color:white']/@href")


def get_urls():
    urls = []
    r = session.get("https://www.ikea.com/pl/pl/stores/")
    tree = html.fromstring(r.text)
    links = tree.xpath("//li/a[@class='pub__link-list__item']/@href")
    for link in links:
        if "-pub" in link:
            urls += get_children(link)
        else:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1[contains(@class, 'pub__h1')]/text()")
    ).strip()

    raw_address = ", ".join(
        tree.xpath(
            "//p[./strong[contains(text(), 'Adres')]]/text()|//p[./strong[contains(text(), 'Adres')] and not(./preceding-sibling::h2)]/following-sibling::p[1]/text()|//h3[text()='Adres']/following-sibling::p/text()"
        )
    ).strip()
    street_address, city, state, postal = get_international(raw_address)

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//p[./strong[contains(text(), 'Godziny')]]/text()|//p[./strong[contains(text(), 'sklepu')]]/following-sibling::p[1]/text()|//p[./strong[contains(text(), 'otwarcia:')]]/following-sibling::p[1]/text()|//h3[text()='Godziny otwarcia']/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    check = ""
    for h in hours:
        line = h[:2]
        if line not in check:
            _tmp.append(h)
        check += h

    hours_of_operation = ";".join(_tmp).replace("*", "")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="PL",
        store_number=SgRecord.MISSING,
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=13) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.ikea.com/pl"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
