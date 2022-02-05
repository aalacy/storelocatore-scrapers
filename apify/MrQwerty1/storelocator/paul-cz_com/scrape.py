from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.paul-cz.com/en/our-stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h1/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h2[contains(text(), 'Contact')]/following-sibling::p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    postal = SgRecord.MISSING
    if line[-1][0].isdigit():
        postal = line.pop()

    city = line.pop().split()[0]
    if len(line) == 2 and line[-1][0].isdigit():
        postal = line.pop()
    street_address = ", ".join(line)
    phone = "".join(
        tree.xpath(
            "//h2[contains(text(), 'Contact')]/following-sibling::p/a[contains(@href, 'tel:')]/text()"
        )
    ).strip()

    try:
        text = "".join(
            tree.xpath("//script[contains(text(), 'var locations')]/text()")
        ).split(", ")
        latitude = text[-2]
        longitude = text[-1].replace("]);", "")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//table[@class='single-shop-opening-hours']//tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]//text()")).strip()
        inter = "".join(h.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp).replace("*", "")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="CZ",
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
    locator_domain = "https://www.paul-cz.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
