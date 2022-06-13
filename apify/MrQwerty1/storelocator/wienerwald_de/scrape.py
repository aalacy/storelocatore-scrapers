from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col-md-6']/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//footer//address/preceding-sibling::h3/text()")
    ).strip()
    line = tree.xpath("//footer//address/text()")
    line = list(filter(None, [li.strip() for li in line]))

    raw_address = ", ".join(line)
    zc = line.pop()
    street_address = ", ".join(line)
    postal = zc.split()[0]
    city = zc.replace(postal, "").strip()
    country_code = "DE"
    phone = (
        "".join(tree.xpath("//a[contains(text(), 'Telefon')]/text()"))
        .replace("Telefon", "")
        .replace(":", "")
        .strip()
    )

    hours = tree.xpath("//h3[contains(text(), 'Unsere')]/following-sibling::a/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
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
    locator_domain = "https://wienerwald.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
