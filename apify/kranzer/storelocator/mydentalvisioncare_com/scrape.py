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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://kidsdentalvisioncare.com/sitemaps-1-section-locations-1-sitemap.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://kidsdentalvisioncare.com/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = (
        "".join(
            tree.xpath(
                '//main//a[contains(@href, "tel")]/preceding-sibling::span/text()'
            )
        )
        or "<MISSING>"
    )
    street_address = ad.split(",")[0].strip()
    city = ad.split(",")[1].strip()
    state = ad.split(",")[2].split()[0].strip()
    postal = ad.split(",")[2].split()[1].strip()
    country_code = "US"
    location_name = (
        " ".join(tree.xpath("//h1/span//text()")).replace("\n", "").strip()
        or "<MISSING>"
    )
    location_name = " ".join(location_name.split())
    phone = (
        "".join(tree.xpath('//main//a[contains(@href, "tel")]/text()')) or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3[contains(text(), "OTHER NEARBY LOCATIONS")]/preceding::ul[1]/li//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    js = "".join(tree.xpath('//div[@class="gm-map"]/@data-dna'))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    j = json.loads(js)
    for coord in j:
        try:
            coord_temp = coord["options"]["infoWindowOptions"]["content"]
        except:
            continue
        coord_tem = html.fromstring(coord_temp)
        coord_temp = "".join(coord_tem.xpath("//*//text()"))
        if postal in coord_temp:
            coord = coord["locations"]
            latitude = str(coord).split("'lat': ")[1].split(",")[0]
            longitude = str(coord).split("'lng': ")[1].split(",")[0]
            break

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
