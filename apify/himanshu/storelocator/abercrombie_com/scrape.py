import json
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
    r = session.get(
        "https://www.abercrombie.com/shop/ViewAllStoresDisplayView?storeId=11203&catalogId=10901&langId=-1",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath('//ul[@class="link-list-arrow"]/li/a/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.abercrombie.com"
    page_url = f"https://www.abercrombie.com{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//meta[@itemprop="streetAddress"]/@content')) or "<MISSING>"
    )
    city = (
        "".join(tree.xpath('//meta[@itemprop="addressLocality"]/@content'))
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath('//meta[@itemprop="addressRegion"]/@content')) or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('//meta[@itemprop="postalCode"]/@content')) or "<MISSING>"
    )
    if postal == "-" or postal == "0000":
        postal = "<MISSING>"
    country_code = (
        "".join(tree.xpath('//meta[@itemprop="addressCountry"]/@content'))
        or "<MISSING>"
    )
    phone = "".join(tree.xpath('//meta[@itemprop="telephone"]/@content')) or "<MISSING>"
    hours_of_operation = ""
    latitude = "".join(tree.xpath("//main/@data-latitude"))
    longitude = "".join(tree.xpath("//main/@data-longitude"))
    store_number = page_url.split("/")[-1].strip()
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "geoNodeUniqueId")]/text()'))
        .split("physicalStore',")[1]
        .split(");")[0]
        .strip()
    )
    js = json.loads(js_block)
    types = js["physicalStoreAttribute"]
    location_type = ""
    for typ in types:
        if typ["name"] == "Brand":
            location_type = typ["value"]
            break

    location_type = location_type.replace("ACF", "abercrombie and fitch").replace(
        "KID", "abercrombie and fitch Kids"
    )
    location_name = location_type
    index = 0
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    for time_period in js["physicalStoreAttribute"][-1]["value"].split(","):
        hours_of_operation += days[index] + " " + time_period.replace("|", " - ") + " "
        index += 1

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
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
