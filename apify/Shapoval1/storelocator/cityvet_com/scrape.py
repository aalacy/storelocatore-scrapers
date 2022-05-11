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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get("https://www.cityvet.com/my-location/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//header/h2/a/@href")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.cityvet.com"
    page_url = url

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    adr = (
        "".join(
            tree.xpath(
                '//span[./i[@class="fas fa-map-marker-alt"]]/following-sibling::span/text()[2]'
            )
        )
        .replace(",", "")
        .strip()
    )

    street_address = " ".join(
        tree.xpath(
            '//span[./i[@class="fas fa-map-marker-alt"]]/following-sibling::span/text()[1]'
        )
    ).strip()
    city = " ".join(adr.split()[:-2])
    state = adr.split()[-2].strip()
    postal = adr.split()[-1].strip()
    country_code = "US"
    location_name = "".join(tree.xpath("//h1/text()"))

    phone = (
        "".join(
            tree.xpath(
                '//span[./i[contains(@class, "fas fa-phone")]]/following-sibling::span/text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find("P") != -1:
        phone = phone.split("P")[1].split("|")[0].strip()
    text = "".join(
        tree.xpath('//li/a[./span[./i[@class="fas fa-map-marker-alt"]]]/@href')
    )
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    hours_of_operation = (
        tree.xpath(
            '//div[./div/h4[contains(text(), "Location")]]/following-sibling::div//ul/li/span/text()'
        )
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = tree.xpath(
            '//div[./div/h4[contains(text(), "Ruffit")]]/following-sibling::div//ul/li/span/text()'
        )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)
    cms = "".join(tree.xpath('//h3[contains(text(), "Coming")]/text()'))
    if cms:
        hours_of_operation = "Coming Soon"
    if hours_of_operation == "Coming Soon":
        latitude, longitude = "<MISSING>", "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
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
        hours_of_operation=hours_of_operation,
        raw_address=f"{street_address} {adr}",
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
