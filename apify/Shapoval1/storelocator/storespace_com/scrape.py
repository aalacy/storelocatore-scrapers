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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get("https://www.storespace.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "storage-locations")]/text()')


def get_data(url, sgw: SgWriter):

    locator_domain = "https://www.storespace.com"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath('//h1[@class="h3 mb-4"]/text()')).replace("\n", "").strip()
    )
    if location_name.find(",") != -1:
        location_name = location_name.split(",")[0].strip()
    ad = "".join(tree.xpath('//td[@class="pt-2"]/text()[2]')).replace("\n", "").strip()
    street_address = (
        "".join(tree.xpath('//td[@class="pt-2"]/text()[1]')).replace("\n", "").strip()
    )
    city = ad.split(",")[0].strip() or "<MISSING>"
    state = ad.split(",")[1].split()[0].strip() or "<MISSING>"
    postal = ad.split(",")[1].split()[1].strip() or "<MISSING>"
    country_code = "US"
    phone = (
        "".join(
            tree.xpath(
                '//p[text()="Location Details"]/following-sibling::table//a[contains(@href, "tel")]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = tree.xpath(
        '//p[text()="Service Hours"]/following-sibling::table[1]//tr//td//text()'
    )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)
    try:
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "var facility")]/text()'))
            .split("lat:")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "var facility")]/text()'))
            .split("lng:")[1]
            .split("};")[0]
            .strip()
        )
    except:
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
