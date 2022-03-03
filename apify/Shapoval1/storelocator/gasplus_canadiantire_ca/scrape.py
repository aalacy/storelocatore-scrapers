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
    r = session.get("https://www.canadiantire.ca/sitemap_0_1.xml.gz", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "/store-details/")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.canadiantire.ca/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    try:
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
    except:
        return
    js_block = "".join(tree.xpath('//div[@class="store-locator"]/@data-config'))
    js = json.loads(js_block)
    location_name = js.get("storeName") or "<MISSING>"
    street_address = js.get("storeAddress1") or "<MISSING>"
    city = js.get("storeCityName") or "<MISSING>"
    state = js.get("storeProvince") or "<MISSING>"
    postal = js.get("storePostalCode") or "<MISSING>"
    country_code = "CA"
    phone = js.get("storeTelephone") or "<MISSING>"
    latitude = js.get("storeLatitude") or "<MISSING>"
    longitude = js.get("storeLongitude") or "<MISSING>"
    hours = tree.xpath('//h2[text()="Store Hours"]/following-sibling::table[1]//tr')
    tmp = []
    for h in hours:
        day = "".join(
            h.xpath(
                './/td[@class="store-locator__store-info__hours-table__day"]/text()'
            )
        )
        js_hours = "".join(h.xpath(".//@data-working-hours"))
        try:
            jsh = json.loads(js_hours)
            opens = jsh.get("open")
            closes = jsh.get("close")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        except:
            time = "".join(h.xpath(".//@data-working-hours"))
            line = f"{day} {time}"
            tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    store_number = js.get("storeNumber")
    location_type = (
        ",".join(
            tree.xpath(
                "//main[@class='store-locator__main']//h2[contains(text(), 'STORE SERVICES')]/following-sibling::ul[1]/li//text()"
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    location_type = " ".join(location_type.split()) or "<MISSING>"

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
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
