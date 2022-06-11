from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.jimsfitness.be/nl/clubs", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='location']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.jimsfitness.be{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    street_address = "".join(
        tree.xpath("//i[@class='fa fa-map']/following-sibling::a/text()")
    ).strip()
    city = "".join(
        tree.xpath("//i[@class='fa fa-map-marker']/following-sibling::span/text()")
    ).strip()
    country_code = "BE"
    phone = "".join(
        tree.xpath("//i[@class='fa fa-phone']/following-sibling::span/text()")
    ).strip()

    text = "".join(tree.xpath("//i[@class='fa fa-map']/following-sibling::a/@href"))
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]
    else:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//h3[contains(text(), 'Openingsuren')]/following-sibling::ul/li//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.jimsfitness.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
