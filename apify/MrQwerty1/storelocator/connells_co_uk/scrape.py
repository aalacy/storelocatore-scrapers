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
    urls = []
    for i in range(1, 50):
        r = session.get(f"https://www.connells.co.uk/branches/page-{i}")
        tree = html.fromstring(r.text)
        urls += tree.xpath(
            "//a[@class='branch-card__action button-secondary button-secondary--red']/@href"
        )

        if len(urls) % 18 != 0:
            break

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.connells.co.uk{slug}"
    r = session.get(page_url)
    try:
        tree = html.fromstring(r.text)
    except:
        return

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = " ".join(
        " ".join(tree.xpath("//p[@itemprop='address']/text()")[1:]).split()
    )
    street_address, city, state, postal = get_international(raw_address)
    text = "".join(tree.xpath("//script[contains(text(), 'var dimensions')]/text()"))
    text = text.split('"branches":[')[1].split("]});")[0]
    phone = "".join(tree.xpath("//div[@class='hero__phone'][1]/a/@href")).replace(
        "tel:", ""
    )

    j = json.loads(text)
    store_number = j.get("branch_id")
    latitude = j.get("lat")
    longitude = j.get("lng")

    _tmp = []
    hours = tree.xpath("//li[@class='opening-time-item']")
    for h in hours:
        day = " ".join(
            "".join(h.xpath("./span[@class='opening-time-day']/text()")).split()
        )
        inter = " ".join(
            "".join(h.xpath("./span[@class='opening-time-value']/text()")).split()
        )
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
        store_number=store_number,
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
    locator_domain = "https://www.connells.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
