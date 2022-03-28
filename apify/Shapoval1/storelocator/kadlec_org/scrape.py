import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.providence.org/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), '/locations/kadlec/')]/text() | //url/loc[contains(text(), '/urgent-care/kadlec')]/text()"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://kadlec.org/"
    page_url = "".join(url)
    if (
        page_url == "https://www.providence.org/locations/kadlec/home-health"
        or page_url == "https://www.providence.org/locations/kadlec/kadlec-clinic"
        or page_url
        == "https://www.providence.org/locations/kadlec/kadlec-st-mary-transfer-center"
    ):
        return
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
    if not js_block:
        return
    js = json.loads(js_block)
    a = js.get("address")
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    postal = "<MISSING>"
    if a:
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    location_name = js.get("name") or "<MISSING>"
    phone = js.get("telephone") or "<MISSING>"
    if str(phone).find("ext") != -1:
        phone = str(phone).split("ex")[0].strip()
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="location-header-info"]/div/div[@class="hours-text text-muted"]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    if hours_of_operation.find("X-Ray") != -1:
        hours_of_operation = hours_of_operation.split("X-Ray")[0].strip()
    if hours_of_operation.find("Phone") != -1:
        hours_of_operation = hours_of_operation.split("Phone")[0].strip()
    try:
        latitude = js.get("geo").get("latitude")
        longitude = js.get("geo").get("longitude")
        location_type = js.get("@type") or "<MISSING>"
    except:
        latitude, longitude, location_type = "<MISSING>", "<MISSING>", "<MISSING>"
    if location_name.find("Kadlec") != -1:
        location_type = "Kadlec"
    if page_url.find("/urgent-care/kadlec/") != -1:
        location_name = (
            "".join(tree.xpath('//div[@class="location-header-info"]/div[1]/h1/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            " ".join(
                tree.xpath(
                    '//div[@class="location-header-info"]/div[1]/div[@class="loc-address"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        city = ad.split(",")[-2].strip()
        state = ad.split(",")[-1].split()[0].strip()
        postal = ad.split(",")[-1].split()[1].strip()
        street_address = " ".join(ad.split(",")[:-2]).strip()
        latitude = (
            "".join(
                tree.xpath('//div[@class="location-header-info"]/div[1]/div/@data-lat')
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                tree.xpath('//div[@class="location-header-info"]/div[1]/div/@data-lng')
            )
            or "<MISSING>"
        )
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="location-header-info"]/div[1]/div[@class="loc-phone"]//text()'
                )
            )
            or "<MISSING>"
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
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
