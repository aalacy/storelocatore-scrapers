from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://www.heartland.bank/LEARNING/FAQs/Entries/what-are-your-current-atm-locations",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath(
        '//h3[text()="What are your current ATM Locations?"]/following::ul[1]/li//a[not(contains(@href, "money"))]/@href'
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.heartland.bank/"
    page_url = url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//p[@class="blueAddress"]/text()[1]'))
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(tree.xpath('//p[@class="blueAddress"]/text()[2]'))
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = (
        "".join(tree.xpath('//p[contains(text(), "Phone:")]/text()[1]'))
        .replace("Phone:", "")
        .strip()
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"latitude":')[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"longitude":')[1]
        .split("}")[0]
        .strip()
    )
    location_type = "ATM"

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
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
