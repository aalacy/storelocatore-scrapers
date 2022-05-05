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
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_city(line):
    adr = parse_address(International_Parser(), line)
    return adr.city


def get_urls():
    urls = []
    r = session.get("https://www.wework.com/search?slug=", headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'window.clientSideInjectionVars')]/text()"
        )
    )
    text = text.split('"buildings":')[1].split('"clientStrings"')[0][:-1]
    js = json.loads(text)
    for j in js:
        country = j.get("207")
        if country == "CN":
            continue
        urls.append((j.get("2"), country))

    return urls


def get_data(param, sgw: SgWriter):
    slug, country_code = param
    page_url = f"https://www.wework.com/buildings/{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    line = "".join(tree.xpath("//address[@class='building-address']/text()")).split(
        "\n"
    )
    line = list(filter(None, [l.strip() for l in line]))

    raw_address = " ".join(" ".join(line).split())
    street_address, city, state, postal = get_international(raw_address)
    if city == SgRecord.MISSING:
        _tmp = ", ".join(raw_address.split(", ")[:-1])
        city = get_city(_tmp)

    cities = {
        "Paris": "Paris",
        "Barcelona": "Barcelona",
        "Madrid": "Madrid",
        "Brooklyn": "New York",
    }
    if not city:
        for k, v in cities.items():
            if k in raw_address:
                city = v
                break

    try:
        phone = tree.xpath(
            "//div[@class='lead-form-contact-footer__inner']//a[contains(@href, 'tel:')]/text()"
        )[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'latitude')]/text()"))
        latitude = text.split('"latitude":"')[1].split('"')[0]
        longitude = text.split('"longitude":"')[1].split('"')[0]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.wework.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
