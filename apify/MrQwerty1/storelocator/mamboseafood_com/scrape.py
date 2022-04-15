from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://mamboseafood.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(text(), 'Locations')]/following-sibling::ul//a/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2/text()")).strip()
    line = tree.xpath("//h2/following-sibling::p[./a][1]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line.pop(0).strip()
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    if "Ste A" in city:
        city = city.replace("Ste A", "")
        street_address = f"{street_address}, Ste A"
    csz = csz.split(",")[1].strip()
    state, postal = csz.split()
    phone = "".join(
        tree.xpath("//h2/following-sibling::p/a[contains(@href, 'tel:')]/text()")
    )
    try:
        text = (
            "".join(tree.xpath("//a[contains(@href, 'daddr=')]/@href"))
            .replace("%20", "")
            .replace("+", "")
        )
        latitude, longitude = eval(text.split("=")[-1])
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//h2/following-sibling::p[./a[contains(@href, 'tel:')]]/following-sibling::p[1]/text()"
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

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://mamboseafood.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
