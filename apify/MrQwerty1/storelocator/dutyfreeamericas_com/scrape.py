from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://dutyfreeamericas.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@id='locations-list-holder']//a[not(contains(@href, '/index'))]/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    street_address = "".join(
        tree.xpath("//span[contains(text(), 'Address')]/following-sibling::span/text()")
    ).strip()
    city = "".join(
        tree.xpath("//span[contains(text(), 'City')]/following-sibling::span/text()")
    ).strip()
    state = "".join(
        tree.xpath("//span[contains(text(), 'State')]/following-sibling::span/text()")
    ).strip()
    postal = (
        "".join(
            tree.xpath("//span[contains(text(), 'Zip')]/following-sibling::span/text()")
        )
        .replace("00000", "")
        .strip()
    )
    country_code = "".join(
        tree.xpath("//span[contains(text(), 'Country')]/following-sibling::span/text()")
    ).strip()
    phone = "".join(
        tree.xpath("//span[@class='amlocator-icon -phone']/following-sibling::a/text()")
    ).strip()
    store_number = "".join(
        tree.xpath(
            "//span[./strong[contains(text(), 'Number')]]/following-sibling::div//text()"
        )
    ).strip()

    text = "".join(tree.xpath("//script[contains(text(), 'locationData')]/text()"))
    try:
        latitude = text.split("lat:")[1].split(",")[0].strip()
        longitude = text.split("lng:")[1].split(",")[0].strip()
        if latitude == "0":
            raise IndexError
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[@class='amlocator-schedule-table']/div")
    for h in hours:
        day = "".join(h.xpath("./span[1]//text()")).strip()
        inter = "".join(h.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
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
    locator_domain = "https://dutyfreeamericas.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
