from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://rundum-akzenta.de/maerkte/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='a-button' and contains(@href, '/maer')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://rundum-akzenta.de{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = " ".join(
        tree.xpath("//h4[./i[contains(@class, 'standort')]]//text()")
    ).strip()
    line = tree.xpath(
        "//h4[./i[contains(@class, 'standort')]]/following-sibling::p[1]/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))
    raw_address = ", ".join(line)
    zc = line.pop()
    street_address = ", ".join(line)
    postal = zc.split()[0]
    city = zc.replace(postal, "").strip()
    if "–" in city:
        city = city.split("–")[0].strip()
    country_code = "DE"
    phone = "".join(
        tree.xpath(
            "//h4[./i[contains(@class, 'standort')]]/following-sibling::p[last()]/text()"
        )
    ).strip()
    text = "".join(tree.xpath("//script[contains(text(), 'var av_google_map')]/text()"))
    latitude = text.split("['lat'] =")[1].split(";")[0].strip()
    longitude = text.split("['long'] =")[1].split(";")[0].strip()

    _tmp = []
    hours = tree.xpath(
        "//h4[./i[contains(@class, 'zeit')]]/following-sibling::p[1]/span"
    )
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()")).strip()
        _tmp.append(f"{day}: {inter}")
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
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
    locator_domain = "https://rundum-akzenta.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
