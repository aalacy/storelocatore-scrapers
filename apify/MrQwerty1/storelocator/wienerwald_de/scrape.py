import ssl
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgselenium import SgChrome


def get_urls():
    with SgChrome() as fox:
        fox.get("https://wienerwald.de/standorte")
        source = fox.page_source
    tree = html.fromstring(source)

    return set(tree.xpath("//a[contains(text(), 'Zum Standort')]/@href"))


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(slug, sgw: SgWriter):
    page_url = f"https://wienerwald.de{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join(tree.xpath("//h1//text()")).strip()
    line = tree.xpath("//address/p[1]/text()")
    street_address = line.pop(0).strip()
    csz = line.pop(0)
    postal = csz.split()[0]
    city = csz.replace(postal, "").strip()

    for p in tree.xpath("//address/p/text()"):
        if "tel" in p.lower():
            phone = (
                p.lower().replace("tel", "").replace(":", "").replace(".", "").strip()
            )
            if "oder" in phone:
                phone = phone.split("oder")[0].strip()
            break
    else:
        phone = SgRecord.MISSING

    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Öffnungszeiten')]/following-sibling::table[1]//tr"
    )
    for h in hours:
        day = "".join(h.xpath("./th//text()")).strip()
        inter = "".join(h.xpath("./td//text()")).strip()
        _tmp.append(f"{day} {inter}")

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
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    locator_domain = "https://wienerwald.de/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
