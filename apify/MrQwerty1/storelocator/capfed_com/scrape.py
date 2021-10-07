from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.capfed.com/locations/branch-locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='location-search__result-name']/@href")


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.capfed.com{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    street_address = ", ".join(
        tree.xpath("//span[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    try:
        phone = tree.xpath("//span[@itemprop='telephone']/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING
    latitude = "".join(tree.xpath("//div[@data-latitude]/@data-latitude"))
    longitude = "".join(tree.xpath("//div[@data-latitude]/@data-longitude"))

    _tmp = []
    hours = tree.xpath(
        "//div[@class='location-details__hours' and ./h2[contains(text(), 'Lobby')]]/text()"
    )
    for h in hours:
        if h.strip():
            _tmp.append(f"{h.strip()}")

    hours_of_operation = ";".join(_tmp)

    if "soon" in location_name.lower():
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type="Branch",
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://www.capfed.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
