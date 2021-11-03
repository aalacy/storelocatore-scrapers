import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.livingspaces.com/stores")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//div[@class='st-detail']/a/@href"))


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.livingspaces.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1//text()")).strip()
    if tree.xpath("//span[contains(text(), 'Coming')]"):
        return
    line = tree.xpath(
        "//div[@class='col-xs-5' and ./a[contains(@href, 'Map')]]/span/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    try:
        store_number = tree.xpath("//a[contains(@href, 'storeId=')]/@href")[0].split(
            "storeId="
        )[-1]
    except IndexError:
        store_number = SgRecord.MISSING

    phone = "".join(tree.xpath("//div[@class='col-xs-3']/span/text()")).strip()
    try:
        j = json.loads(
            "".join(tree.xpath("//script[contains(text(), 'FurnitureStore')]/text()"))
        )
        latitude = j["geo"]["latitude"]
        longitude = j["geo"]["longitude"]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    if latitude == SgRecord.MISSING:
        text = "".join(
            tree.xpath(
                "//script[contains(text(), 'https://www.google.com/maps/')]/text()"
            )
        )
        if text:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]

    hours_of_operation = tree.xpath(
        "//div[@class='col-xs-5' and ./span[contains(text(), 'Hours')]]/span//text()"
    )[1]

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.livingspaces.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
