from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.decathlon.com/sitemap_pages_1.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    if not tree.xpath("//h4[contains(text(), 'Location')]"):
        return

    location_name = "".join(tree.xpath("//div[@class='shg-row']//h2/text()")).strip()
    line = tree.xpath(
        "//div[./div/h4[contains(text(), 'Location')]]/following-sibling::div[1]//text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line.pop(0)
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state, postal = csz.split()

    phones = tree.xpath(
        "//div[./div/h4[contains(text(), 'Contact')]]/following-sibling::div[1]//text()"
    )
    phones = list(filter(None, [p.strip() for p in phones]))
    phone = phones.pop(0)

    latitude = "".join(tree.xpath("//div[@data-latitude]/@data-latitude"))
    longitude = "".join(tree.xpath("//div[@data-longitude]/@data-longitude"))

    _tmp = []
    hours = tree.xpath(
        "//div[./div/h4[contains(text(), 'Hours')]]/following-sibling::div[1]//text()"
    )
    for h in hours:
        if not h.strip():
            continue
        _tmp.append(h.strip())

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
    locator_domain = "https://www.decathlon.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
