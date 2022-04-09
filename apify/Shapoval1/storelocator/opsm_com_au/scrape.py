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
    r = session.get("https://www.opsm.com.au/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    tmp = []
    div = tree.xpath("//*//text()")
    for d in div:
        if "/stores" not in d:
            continue
        slug = "".join(d).replace("\n", "").strip()
        tmp.append(slug)
    return tmp


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.opsm.com.au/"
    page_url = f"https://www.opsm.com.au{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ad = "".join(tree.xpath('//div[@class="w-100"]/p[1]/text()')) or "<MISSING>"
    if ad == "<MISSING>":
        return
    street_address = " ".join(ad.split(",")[:-3]).strip()
    city = ad.split(",")[-3].strip()
    state = ad.split(",")[-2].strip()
    postal = ad.split(",")[-1].strip()
    country_code = "AU"
    latitude = (
        "".join(tree.xpath('//input[@id="storedetails_latitude"]/@value'))
        or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath('//input[@id="storedetails_longitude"]/@value'))
        or "<MISSING>"
    )
    location_name = "".join(tree.xpath('//h4[@class="mb-3"]//text()')) or "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                '//span[contains(text(), "Tel")]/following-sibling::span//text()'
            )
        )
        or "<MISSING>"
    )
    block = (
        "".join(tree.xpath('//script[contains(text(), "openingHours")]/text()'))
        .split("let store = ")[1]
        .split("let open")[0]
        .strip()
    )
    store_number = page_url.split("/")[-1].strip()
    try:
        js_block = block.split('"openingHours":')[1].split("],")[0].strip()
        js_block = '{"openingHours":' + js_block + "]}"
        js_block = " ".join(js_block.split())
        js = eval(js_block)
        hours = js.get("openingHours")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                day = h.get("day")
                times = h.get("time")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
    except:
        hours_of_operation = "<MISSING>"

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
