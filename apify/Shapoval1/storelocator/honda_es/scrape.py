from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    api_urls = [
        "https://www.honda.at/cars/sitemap.xml",
        "https://www.honda.hu/cars/sitemap.xml",
        "https://www.honda.nl/cars/sitemap.xml",
        "https://auto.honda.fr/cars/sitemap.xml",
        "https://www.honda.no/cars/sitemap.xml",
        "https://www.honda.lu/cars/sitemap.xml",
        "https://www.honda.pl/cars/sitemap.xml",
        "https://www.fr.honda.be/cars/sitemap.xml",
        "https://www.honda.dk/cars/sitemap.xml",
        "https://www.honda.es/cars/sitemap.xml",
        "https://www.fr.honda.ch/cars/sitemap.xml",
    ]
    tmp = []
    for api_url in api_urls:
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.content)
        page_urls = tree.xpath(
            "//url/loc[contains(text(), '/cars/dealers/')] | //url/loc[contains(text(), '/cars/concessionnaires/')] | //url/loc[contains(text(), '/cars/concesionarios/')] | //url/loc[contains(text(), '/cars/concessionnaire/')]"
        )
        for a in page_urls:
            page_url = "".join(a.xpath(".//text()"))
            tmp.append(page_url)
    return tmp


def get_data(url, sgw: SgWriter):
    locator_domain = "https://honda.es/"
    page_url = "".join(url)
    if page_url.find("industrie.") != -1:
        page_url = page_url.replace("industrie.", "auto.")
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    street_address = " ".join(street_address.split())
    city = (
        "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    country_code = page_url.split("honda.")[1].split("/")[0].upper()
    location_name = (
        "".join(tree.xpath("//h1/text()")).replace("\n", "").strip() or "<MISSING>"
    )
    phone = (
        "".join(
            tree.xpath(
                '//section[.//h1]/following-sibling::section[1]//a[contains(@href, "tel")]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        (
            "".join(
                tree.xpath(
                    '//section[.//h1]/following-sibling::section[2]//a[contains(@href, "tel")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
    if phone.find("E-mail") != -1:
        phone = phone.split("E-mail")[0].strip()
    if phone.find("w") != -1:
        phone = phone.split("w")[0].strip()
    text = "".join(tree.xpath('//div[@class="dealer-map"]/a/@href'))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    if latitude == "0.0":
        latitude, longitude = "<MISSING>", "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//section[.//h1]/following-sibling::section[.//*[@class="timings"]][1]//*[@class="timings"]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=f"{street_address} {city} {postal}",
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
