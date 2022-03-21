from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.exhalespa.com/locations", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='loc-locations']//li/a/@href")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].split("!")[0]
        longitude = text.split("!2d")[1].split("!")[0]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.exhalespa.com{url}"
    if "virtual-" in page_url or "bermuda" in page_url:
        return

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1/text()|//div[@class='location_banner']//h2/text()")
    ).strip()
    line = tree.xpath("//div[@class='address']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = "".join(tree.xpath("//span[@class='phone']/a/text()")).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    days = tree.xpath("//div[@class='text']")[0].xpath(
        ".//p/strong/text()|.//span/strong/text()"
    )
    times = tree.xpath("//div[@class='text']")[0].xpath(".//p/text()|.//span/text()")
    times = list(filter(None, [t.strip() for t in times]))

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

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
    locator_domain = "https://exhalespa.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
