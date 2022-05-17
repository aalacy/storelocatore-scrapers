from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://fabricland.ca/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)

    for u in tree.xpath("//loc[contains(text(), 'storelocator')]/text()"):
        if u.count("/") == 6:
            urls.append(u)

    return urls


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//title/text()")).split("Store")[0].strip()
    line = tree.xpath(
        "//div[img[contains(@src, 'pin.')]]/following-sibling::div[1]/p/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))

    city, state = line.pop().split(", ")
    street_address = ", ".join(line)
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()
    if street_address.endswith(","):
        street_address = street_address[:-1]
    country_code = "CA"
    phone = "".join(tree.xpath("//a[@class='pnumber']/text()")).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath("//div[span[@class='store__days']]")
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "".join(h.xpath("./following-sibling::div[1]//text()")).strip()
        _tmp.append(f"{day}: {inter}")
        if "Sunday" in day:
            break

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        country_code=country_code,
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
    locator_domain = "https://fabricland.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
