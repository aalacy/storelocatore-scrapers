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


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.content)


def get_urls():
    urls = set()
    root = get_tree("https://friendlygrocer.com.au/sitemap.xml")
    states = root.xpath("//loc[contains(text(), '/find-a-store/')]/text()")
    for state in states:
        tree = get_tree(state)
        links = tree.xpath("//div[@class='row']//a/@href")
        for link in links:
            urls.add(f"https://friendlygrocer.com.au{link}")

    return urls


def get_data(page_url, sgw: SgWriter):
    tree = get_tree(page_url)

    location_name = "".join(tree.xpath("//div[@class='row']//h3[1]/text()")).strip()
    raw_address = "".join(tree.xpath("//div[@class='row']//p/span/text()")).strip()
    if raw_address == ",":
        raw_address = ""
    if " Q " in raw_address:
        raw_address = raw_address.replace(" Q ", " Qld ")

    street_address, city, state, postal = get_international(raw_address)
    if city == SgRecord.MISSING:
        city = raw_address.split(", ")[-1].strip()
        if state:
            city = city.split(state)[0].strip()
        if "A.c.t." in city:
            city = city.split("A.c.t.")[0]
        if not city and raw_address.count(",") == 2:
            city = raw_address.split(",")[-2]
        if "Lot " in city:
            city = raw_address.split(",")[0].strip()
    country_code = "AU"

    text = "".join(tree.xpath("//script[contains(text() ,'.LatLng')]/text()"))
    try:
        latitude, longitude = eval(text.split(".LatLng")[1].split(";")[0])
        if latitude == 0.0:
            raise
    except:
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
    locator_domain = "https://friendlygrocer.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
