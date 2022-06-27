from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.mytoys.de/c/filialen.html", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(@href, '/c/filiale')]/@href")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.mytoys.de{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='content-headline content-headline--line-']/h1/text()")
    ).strip()
    line = tree.xpath(
        "//h2[contains(text(), 'Anschrift')]/following-sibling::p[1]/text()"
    )
    raw_address = ", ".join(line)
    street_address = ", ".join(line[:-1])
    cp = line.pop()
    postal = cp.split()[0]
    city = cp.replace(postal, "").strip()
    phone = (
        "".join(tree.xpath("//p[contains(text(), 'Tel')]//text()"))
        .replace("Tel", "")
        .replace(":", "")
        .replace(".", "")
        .strip()
    )

    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Öffnungszeiten')]/following-sibling::p/text()"
    )
    for h in hours:
        if "2022" in h or "!" in h:
            break
        if not h.strip():
            continue
        _tmp.append(h.strip())

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="DE",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.mytoys.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
