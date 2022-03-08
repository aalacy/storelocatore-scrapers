from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://californiasun.com/page-sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc[contains(text(), '/locations/')]/text()")
    for link in links:
        if link.count("/") == 5:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='location-title']/text()")).strip()
    line = tree.xpath("//div[@class='location-address']//text()")
    line = list(filter(None, [l.strip() for l in line]))
    csz = line.pop().replace(",", "").split()
    postal = csz.pop()
    state = csz.pop()
    city = " ".join(csz)
    street_address = ", ".join(line)
    phone = "".join(tree.xpath("//div[@class='location-phone']//text()")).strip()

    _tmp = []
    hours = tree.xpath("//div[@class='location-hours']//text()")
    for h in hours:
        if not h.strip() or "Hours" in h:
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
    locator_domain = "https://californiasun.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
