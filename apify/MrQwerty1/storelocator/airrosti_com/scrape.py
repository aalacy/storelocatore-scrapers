from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.airrosti.com/listings/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//h5/a[contains(@href, 'location')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//a[contains(@href, 'maps.google.com')]//span/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    try:
        phone = tree.xpath(
            "//span[./i[@class='fas fa-phone-alt']]/following-sibling::span/text()"
        )[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    text = "".join(tree.xpath("//a[contains(@href, 'maps.google.com')]/@href"))
    try:
        latitude, longitude = text.split("daddr=")[1].split(",")
        if "http" in longitude:
            longitude = longitude.split("http")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//div[@class='elementor-shortcode']/div[contains(@class, 'weekDay')]"
    )
    for h in hours:
        day = "".join(h.xpath("./span[1]/text()")).strip()
        inter = "".join(h.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
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
    locator_domain = "https://www.airrosti.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
