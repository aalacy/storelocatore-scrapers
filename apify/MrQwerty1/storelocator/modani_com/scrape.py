from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.modani.com/store-locations")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//div[@class='store_time_info']//a/@href"))


def get_data(slug, sgw: SgWriter):
    if slug.startswith("{"):
        return
    page_url = f"https://www.modani.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='store_box_title']/text()")
    ).strip()
    line = tree.xpath(
        "//div[@class='store_box_address']/text()|//div[@class='store_box_address']/span/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    if "2nd\xa0Floor" in line:
        line = line[: line.index("2nd\xa0Floor")]
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = "".join(tree.xpath("//span[@class='telephone']/text()")).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude = text.split("!3d")[1].split("!")[0]
    longitude = text.split("!2d")[1].split("!")[0]
    hours = tree.xpath(
        "//div[@class='store_box_time']/text()|//div[@class='store_box_time']/following-sibling::text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.modani.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
