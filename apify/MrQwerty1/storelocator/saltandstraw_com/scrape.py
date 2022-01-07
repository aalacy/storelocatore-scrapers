from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://saltandstraw.com/pages/locations")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(text(), 'LEARN MORE')]/@href"))


def get_data(url, sgw: SgWriter):
    if url.startswith("/"):
        page_url = f"https://saltandstraw.com{url}"
    else:
        page_url = url

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = []
    lines = tree.xpath(
        "//div[@class='shg-rich-text shg-theme-text-content' and count(./p)>=2]//text()"
    )
    for l in lines:
        if not l.strip() or ":" in l:
            continue
        line.append(l.strip())
    line = list(filter(None, [l.strip() for l in line]))
    if not line[0][0].isdigit():
        line.pop(0)

    street_address = ", ".join(line[:-1])
    adr = line[-1]
    city = adr.split(",")[0].strip()
    adr = adr.split(",")[1].strip()
    state = adr.split()[0]
    try:
        postal = adr.split()[1]
    except IndexError:
        postal = SgRecord.MISSING
    phone = "".join(
        tree.xpath(
            "//a[contains(@href, 'tel:') or contains(@href, '(')]//text()|//p[.//span[contains(@aria-label, 'Phone')]]//text()"
        )
    ).strip()
    latitude = "".join(tree.xpath("//div[@data-latitude]/@data-latitude"))

    longitude = "".join(tree.xpath("//div[@data-longitude]/@data-longitude"))

    hours = tree.xpath(
        "//div[./div/div[contains(@class, 'clock')]]/following-sibling::div//text()|//div[./div/i[contains(@class, 'clock')]]/following-sibling::div//text()"
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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://saltandstraw.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
