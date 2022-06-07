from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_children(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@style='background-color:white']/@href")


def get_urls():
    urls = []
    r = session.get("https://www.ikea.com/pl/pl/stores/")
    tree = html.fromstring(r.text)
    links = tree.xpath("//li/a[@class='pub__link-list__item']/@href")
    for link in links:
        if "-pub" in link:
            urls += get_children(link)
        else:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1[contains(@class, 'pub__h1')]/text()")
    ).strip()

    line = tree.xpath("//*[contains(text(), 'Adres')][1]/following::*[1]/text()")
    line = list(filter(None, [li.strip() for li in line]))
    if "IKEA" in line[0]:
        line.pop(0)
    if len(line) > 4:
        line = line[:2]
    if line[0][-1].isalpha() and "ul." not in line[0]:
        line.pop(0)

    raw_address = ", ".join(line)
    street_address = line.pop(0)
    zc = line.pop()
    postal = zc.split()[0]
    city = zc.replace(postal, "").strip()
    if not city:
        city = location_name.replace("IKEA", "").strip()

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//p[./strong[contains(text(), 'Godziny')]]/text()|//p[./strong[contains(text(), 'sklepu')]]/following-sibling::p[1]/text()|//p[./strong[contains(text(), 'otwarcia:')]]/following-sibling::p[1]/text()|//h3[text()='Godziny otwarcia']/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    check = ""
    for h in hours:
        line = h[:2]
        if line not in check:
            _tmp.append(h)
        check += h

    if not _tmp:
        hours = tree.xpath(
            "//h2[text()='Sklep']/following-sibling::dl//text()|//h3[./strong[contains(text(), 'otwarcia')]]/following-sibling::p//text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))

        for day, inter in zip(hours[::2], hours[1::2]):
            _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp).replace("*", "")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="PL",
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://www.ikea.com/pl"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
