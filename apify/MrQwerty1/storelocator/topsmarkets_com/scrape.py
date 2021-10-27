from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_states():
    r = session.get("https://www.topsmarkets.com/StoreLocator/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col-md-9']//a[contains(@href, '.las')]/@href")


def get_urls():
    urls = []
    states = get_states()

    for state in states:
        state = state.replace("..", "https://www.topsmarkets.com")
        r = session.get(state)
        tree = html.fromstring(r.text)
        urls += tree.xpath("//a[text()='View']/@href")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    location_name = "".join(
        tree.xpath("//div[@class='gmap-responsive']/following-sibling::h3/text()")
    ).strip()
    try:
        phone = tree.xpath("//p[@class='PhoneNumber']/a/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING
    store_number = page_url.split("L=")[1].split("&")[0]
    text = "".join(tree.xpath("//script[contains(text(), 'initializeMap')]/text()"))
    latitude, longitude = eval(text.split("initializeMap")[1].split(";")[0])
    if tree.xpath("//dt[contains(text(), 'Pharmacy')]"):
        hours_of_operation = ";".join(
            tree.xpath(
                "//dt[contains(text(), 'Pharmacy')]/preceding-sibling::dd/text()"
            )
        )
    else:
        hours_of_operation = ";".join(tree.xpath("//dd/text()"))

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
    locator_domain = "https://www.topsmarkets.com"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
