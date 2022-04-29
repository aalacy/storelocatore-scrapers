import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.jollibee.uk/findus")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'VIEW MORE')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.jollibee.uk{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//div[@class='row sqs-row' and ./div[@class='col sqs-col-3 span-3']]/div[1]//p//text()"
    )
    if not line:
        line = tree.xpath(
            "//div[@class='col sqs-col-6 span-6']//div[@class='sqs-block-content']/p/text()"
        )
    line = list(filter(None, [li.strip() for li in line]))

    check = line[-1]
    phone = SgRecord.MISSING
    if check[0].isdigit() and check[-1].isdigit():
        phone = line.pop()
    postal = line.pop()
    city = line.pop()
    state = SgRecord.MISSING
    if ", " in city:
        city, state = city.split(", ")
    street_address = line.pop(0)

    text = "".join(
        tree.xpath(
            "//div[@data-block-json and contains(@data-block-json, 'markerLat')]/@data-block-json"
        )
    )
    j = json.loads(text)["location"]
    latitude = j.get("markerLat")
    longitude = j.get("markerLng")

    _tmp = []
    hours = tree.xpath(
        "//div[@class='row sqs-row' and ./div[@class='col sqs-col-3 span-3']]/div[2]//p/strong"
    )
    for h in hours:
        inter = "".join(h.xpath("./text()")).strip()
        day = "".join(h.xpath("./preceding-sibling::text()[1]")).strip()
        _tmp.append(f"{day} {inter}")

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
    locator_domain = "https://www.jollibee.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
