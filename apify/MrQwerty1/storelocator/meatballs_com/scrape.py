from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_urls():
    urls = []
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)
    slugs = tree.xpath("//a[text()='Locations']/following-sibling::ul//a/text()")
    for s in slugs:
        slug = s.lower().replace(", ", "-")
        urls.append(f"https://www.meatballs.com/locations/{slug}/")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2/text()")).strip()
    line = tree.xpath("//div[@class='address-info']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    phone = SgRecord.MISSING
    cnt = 0
    for l in line:
        if "Tel" in l:
            phone = l.replace("Tel:", "").split("Fax")[0].strip()
            break
        cnt += 1

    hours = tree.xpath("//div[@class='address-info']/p[last()]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    if not hours:
        hours = line[cnt + 1 :]
    hours_of_operation = ";".join(hours)

    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

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
    locator_domain = "https://www.meatballs.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
