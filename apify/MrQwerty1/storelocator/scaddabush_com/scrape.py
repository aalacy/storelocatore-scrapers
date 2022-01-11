from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.scaddabush.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='locationsbutton' and not(contains(@href, '/promotions'))]/@href"
    )


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(page_url, sgw: SgWriter):
    if page_url.startswith("/"):
        page_url = f"https://www.scaddabush.com{page_url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    line = tree.xpath(
        "//h4[contains(text(), 'Information')]/following-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    postal = line.pop()
    street_address = line.pop(0)
    if street_address.endswith(","):
        street_address = street_address[:-1]
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    state = line.split(",")[1].strip()
    country_code = "CA"
    phone = "".join(
        tree.xpath(
            "//h4[contains(text(), 'Information')]/following-sibling::p/a/text()"
        )
    ).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath(
        "//p[./b[text()='Hours']]/following-sibling::p//text()|//p[./strong[text()='Hours']]/following-sibling::p//text()"
    )
    for h in hours:
        if "hours" in h.lower():
            break
        if not h.strip():
            continue
        _tmp.append(h.strip())

    hours_of_operation = " ".join(_tmp).replace("pm ", "pm;").replace("pm;–", "pm –")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
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
    locator_domain = "https://www.scaddabush.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
