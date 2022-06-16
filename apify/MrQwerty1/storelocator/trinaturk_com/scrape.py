from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].split("!")[0]
        longitude = text.split("!2d")[1].split("!")[0]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_urls():
    r = session.get("https://www.trinaturk.com/pages/boutiques")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'more information')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).split("-")[-1].strip()
    line = tree.xpath("//b[contains(text(), 'Address')]/following-sibling::a[1]/text()")
    street_address = line.pop(0).strip()
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state, postal = csz.split()
    ph = tree.xpath("//b[contains(text(), 'Phone')]/following-sibling::text()")
    ph = list(filter(None, [p.strip() for p in ph]))
    phone = ph.pop(0)
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath("//h2[contains(text(), 'HOURS')]/following-sibling::p/b")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = (
            "".join(h.xpath("./following-sibling::text()[1]")).replace("*", "").strip()
        )
        _tmp.append(f"{day}: {inter}")

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
    locator_domain = "https://www.trinaturk.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
