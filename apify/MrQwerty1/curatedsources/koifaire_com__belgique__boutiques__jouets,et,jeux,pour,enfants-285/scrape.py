from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    amount, cnt = 40, 0
    while amount == 40:
        api = f"https://www.koifaire.com/belgique/boutiques/jouets,et,jeux,pour,enfants-285/{cnt}/"
        r = session.get(api, headers=headers)
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[@class='titrelist' and img]/@href")
        urls += links
        amount = len(links)
        cnt += 40

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1//text()")).strip()
    line = tree.xpath(
        "//h2[contains(text(), 'Adresse')]/following-sibling::div[1]/font/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))
    raw_address = ", ".join(line)

    zc = line.pop()
    postal = zc.split()[0]
    city = zc.replace(postal, "").strip()
    if "(" in city:
        city = city.split("(")[0].strip()

    street_address = ", ".join(line)
    country_code = "BE"
    phone = (
        "".join(tree.xpath("//div[contains(text(), 'Tel')]/text()"))
        .replace("Tel", "")
        .replace(":", "")
        .strip()
    )
    store_number = page_url.split("-")[-1].replace(".html", "")

    text = "".join(tree.xpath("//font[contains(text(), 'Latitude')]/text()"))
    try:
        latitude = text.split(",")[0].replace("Latitude", "").strip()
        longitude = text.split(",")[-1].replace("Longitude", "").strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Horaires')]/following-sibling::div[1]//tr"
    )
    for h in hours:
        day = "".join(h.xpath("./td[1]//text()")).strip()
        inter = "".join(h.xpath("./td[2]//text()")).strip()
        if inter:
            _tmp.append(f"{day}: {inter}")
        if "Dimanche" in day:
            break

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
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
    locator_domain = "https://www.koifaire.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
