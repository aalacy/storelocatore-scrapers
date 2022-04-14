from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_urls():
    urls = []
    r = session.get('https://www.maersk.com/api_sc9/local-info/offices', headers=headers)
    js = r.json()['data']

    for j in js:
        slug = j.get('lookupUrl')
        urls.append(f'https://www.maersk.com{slug}')

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ids = tree.xpath("//li[contains(@class, '--office')]/button/@data-id")

    for _id in ids:
        d = tree.xpath(f"//div[@id='{_id}']")[0]
        location_type = ''.join(d.xpath(".//div[@class='p-section__find-an-office__detail__title']/text()")).strip()
        location_name = ''.join(d.xpath(".//div[@class='p-section__find-an-office__detail__location']/text()")).strip()
        raw_address = ' '.join(d.xpath(".//div[@class='p-section__find-an-office__detail__address']/text()")).strip()
        try:
            phones = d.xpath(".//div[@class='p-section__find-an-office__detail__tel']/text()")
            phones = list(filter(None, [p.strip() for p in phones]))
            phone = phones[0]
            if '/' in phone:
                phone = phone.split('/')[0]
        except IndexError:
            phone = SgRecord.MISSING

        street_address, city, state, postal = get_international(raw_address)
        country_code = page_url.split('/')[-1].title()

        text = ''.join(d.xpath(".//a[contains(@href, '/place/')]/@href"))
        try:
            latitude, longitude = text.split('/place/')[1].split(',')
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        hours = d.xpath(".//div[@class='p-section__find-an-office__detail__hours']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            location_type=location_type,
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
    locator_domain = "https://www.maersk.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))) as writer:
        fetch_data(writer)
