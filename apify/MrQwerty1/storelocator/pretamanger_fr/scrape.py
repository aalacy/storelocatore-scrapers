from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def generate_links():
    r = session.get("https://locations.pretamanger.fr/index.json")
    js = r.json()["directoryHierarchy"]
    urls = list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://locations.pretamanger.fr/{state['url']}"
        else:
            yield from get_urls(children)


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@id='location-name']/text()"))
    a = tree.xpath("//div[@class='Core-address Core-address--desktop']")[0]
    street_address = ", ".join(
        a.xpath(".//span[contains(@class, 'c-address-street-1')]/text()")
    )
    city = "".join(a.xpath(".//span[@class='c-address-city']/text()")).strip()
    postal = "".join(a.xpath(".//span[@class='c-address-postal-code']/text()")).strip()
    country_code = "".join(
        a.xpath(".//abbr[@class='c-address-country-name c-address-country-fr']/text()")
    ).strip()
    phone = "".join(tree.xpath("//div[@id='phone-main']/text()")).strip()
    latitude = "".join(a.xpath(".//meta[@itemprop='latitude']/@content"))
    longitude = "".join(a.xpath(".//meta[@itemprop='longitude']/@content"))

    _tmp = []
    hours = tree.xpath("//tr[@itemprop='openingHours']")
    for h in hours:
        day = "".join(h.xpath("./td[1]//text()")).strip()
        inter = " ".join("".join(h.xpath("./td[2]//text()")).split())
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
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
    urls = generate_links()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.pretamanger.fr/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
