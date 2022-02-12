import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(
        "https://ioraprimarycare.com/find-a-location/#washington", headers=headers
    )
    tree = html.fromstring(r.text)
    return tree.xpath('//li[@class="clinic-location"]/a/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://ioraprimarycare.com"
    page_url = url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()[2]")).strip()

    street_address = "".join(
        tree.xpath('//div[@id="locations-details"]/h2[1]/text()[1]')
    )
    ad = (
        "".join(tree.xpath('//div[@id="locations-details"]/h2[1]/text()[2]'))
        .replace("\n", "")
        .strip()
    )

    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    js_block = "".join(tree.xpath('//script[contains(text(), "New Patients")]/text()'))
    js = json.loads(js_block)
    phone = js.get("telephone") or "<MISSING>"
    location_type = "".join(tree.xpath("//h1/text()[1]")).replace(":", "").strip()
    hours_of_operation = (
        " ".join(
            tree.xpath('//p[text()="Practice Hours:"]/following-sibling::p/text()')
        )
        .replace("\n", "")
        .strip()
    )
    latitude = (
        "".join(tree.xpath('//script[@id="simple-locator-single-js-extra"]/text()'))
        .split('latitude":"')[1]
        .split('"')[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[@id="simple-locator-single-js-extra"]/text()'))
        .split('longitude":"')[1]
        .split('"')[0]
        .strip()
    )

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
        hours_of_operation=hours_of_operation,
        raw_address=f"{street_address} {ad}",
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
