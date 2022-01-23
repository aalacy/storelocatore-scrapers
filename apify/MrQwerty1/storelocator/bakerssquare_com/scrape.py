from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.bakerssquare.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h3[@class='heading']/following-sibling::ul/li/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if not location_name:
        return
    street_address = "".join(
        tree.xpath("//span[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    phone = "".join(tree.xpath("//span[@itemprop='phone']/a/text()")).strip()

    text = "".join(tree.xpath("//script[contains(text(),'map_options')]/text()"))
    try:
        latitude = text.split("lat:")[1].split(",")[0].strip()
        longitude = text.split("lng:")[1].split("}")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    days = tree.xpath("//ul[@class='hours']/li/span/text()")
    times = tree.xpath("//ul[@class='hours']/li/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.bakerssquare.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
