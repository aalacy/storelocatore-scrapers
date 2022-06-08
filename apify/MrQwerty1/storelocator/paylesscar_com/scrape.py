from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    urls = []
    start = [
        "https://www.paylesscar.com/en/locations/international",
        "https://www.paylesscar.com/en/locations/us",
    ]

    for s in start:
        r = session.get(s, headers=headers, cookies=cookies)
        tree = html.fromstring(r.text)
        urls += tree.xpath("//a[@class='pl-loc-subtitle']/@href")

    return urls


def remove_comma(text: str):
    if text.endswith(","):
        return text[:-1]

    return text


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.paylesscar.com{slug}"
    r = session.get(page_url, headers=headers)
    if r.status_code == 404:
        return
    tree = html.fromstring(r.text)
    location_name = tree.xpath("//span[@itemprop='name']/text()")[-1].strip()
    street_address = ", ".join(
        tree.xpath("//p[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country = "".join(tree.xpath("//p[@itemprop='addressCountry']/text()")).strip()
    phone = "".join(tree.xpath("//p[@itemprop='telephone']//text()")).strip()
    latitude = "".join(tree.xpath("//meta[@itemprop='latitude']/@content"))
    longitude = "".join(tree.xpath("//meta[@itemprop='longitude']/@content"))
    location_type = "".join(
        tree.xpath(
            "//div[./strong[contains(text(), 'Type')]]/following-sibling::div[1]/text()"
        )
    ).strip()
    hours = tree.xpath(
        "//div[./strong[contains(text(), 'Hours')]]/following-sibling::div[1]//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=remove_comma(city),
        state=remove_comma(state),
        zip_postal=postal,
        country_code=country,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
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
    locator_domain = "https://www.paylesscar.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "userName": "PAYLESSCOM",
        "password": "PAYLESSCOM",
        "channel": "Digital",
        "domain": "us",
        "locale": "en",
        "bookingType": "car",
        "deviceType": "bigbrowser",
        "Connection": "keep-alive",
        "Referer": "https://www.paylesscar.com/en/locations/us/al/birmingham/bhm",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    cookies = {
        "APISID": "dfca6acd-74bd-453a-a18d-7a8e09b4b936",
        "DIGITAL_TOKEN": "c38112dc-2768-4aa2-b361-78551d53c8f3-01-cdal-ho5319",
        "datacenter": "cdal",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
