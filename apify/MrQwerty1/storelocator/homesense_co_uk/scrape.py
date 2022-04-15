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
    street = f"{adr.street_address_1} {adr.street_address_2}".replace(
        "None", ""
    ).strip()
    city = adr.city

    return street, city


def get_urls():
    urls = []
    r = session.get("https://www.homesense.com/find-a-store")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'ajaxPageState')]/text()"))
    text = text.split('"markers":')[1].split("}}]")[0] + "}}]"
    js = json.loads(text)
    for j in js:
        source = j.get("text") or "<html></html>"
        root = html.fromstring(source)
        urls.append("".join(root.xpath("//a[@class='view-store-info']/@href")))

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.homesense.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    try:
        d = tree.xpath("//div[@class='store-details-panel']")[0]
    except:
        return

    location_name = "".join(d.xpath(".//h2[@itemprop='name']/text()")).strip()
    adr1 = "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
    adr2 = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
    adr = f"{adr1} {adr2}"
    street_address, city = get_international(adr)
    postal = "".join(d.xpath(".//span[@itemprop='zipCode']/text()")).strip()
    phone = "".join(d.xpath(".//p[@itemprop='telephone']/text()")).strip()
    hours_of_operation = "".join(
        d.xpath(".//span[@itemprop='openingHours']/text()")
    ).strip()
    geo = d.xpath("./preceding-sibling::div[1]")[0]
    latitude = "".join(geo.xpath("./@data-latitude"))
    longitude = "".join(geo.xpath("./@data-longitude"))
    store_number = "".join(geo.xpath("./@data-store-id"))

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="GB",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.homesense.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
