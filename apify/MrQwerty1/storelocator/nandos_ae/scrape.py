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
    postal = adr.postcode or ""

    return street_address, city, state, postal


def get_urls():
    urls = []
    start = [
        "https://www.nandos.com.bh/eat/restaurants-all",
        "https://www.nandosindia.com/eat/restaurants-all",
        "https://www.nandosoman.com/eat/restaurants-all",
        "https://www.nandos.pk/eat/restaurants-all",
        "https://www.nandos.qa/eat/restaurants-all",
        "https://www.nandos.ae/eat/restaurants-all",
        "https://www.nandos.co.zm/eat/restaurants-all",
        "https://www.nandos.co.zw/eat/restaurants-all",
    ]

    for s in start:
        base = s.split("/eat/")[0]
        r = session.get(s)
        tree = html.fromstring(r.text)
        links = tree.xpath(
            "//a[contains(@href, '/eat/restaurant/') or contains(@href, '/eat/restaurants/') and not(contains(@href, '/all'))]/@href"
        )
        for link in links:
            urls.append(f"{base}{link}".strip())

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if "(" in location_name:
        location_name = location_name.split("(")[0].strip()

    locator_domain = page_url.split("/eat/")[0]
    country = page_url.split(".")[-1].split("/")[0].upper()
    if country == "COM":
        if "india" in page_url:
            country = "IN"
        else:
            country = "OM"

    raw_address = "".join(
        tree.xpath("//h1/following-sibling::ul/li[1]//text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    if postal == "" and raw_address[-1].isdigit():
        postal = raw_address.split(",")[-1].strip()
    if city == "" and country != "AE":
        city = raw_address.split(",")[-2].strip()
    if (city == "" and country == "AE") or "Area" in city:
        city = raw_address.split(",")[-1].strip()

    phone = "".join(tree.xpath("//h1/following-sibling::ul/li[2]//text()"))
    latitude = (
        "".join(tree.xpath("//div[@data-lat]/@data-lat"))
        .replace("°", ".")
        .replace("'", "")
        .replace('"N', "")
    )
    longitude = (
        "".join(tree.xpath("//div[@data-lat]/@data-lng"))
        .replace("°", ".")
        .replace("'", "")
        .replace('"E', "")
    )

    _tmp = []
    hours = tree.xpath(
        "//h3[contains(text(), 'Opening')]/following-sibling::ul/li/text()"
    )
    for h in hours:
        if not h.strip():
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
        country_code=country,
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
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
