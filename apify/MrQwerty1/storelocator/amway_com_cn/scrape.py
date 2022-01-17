from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, postal=""):
    if not postal:
        adr = parse_address(International_Parser(), line)
    else:
        adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_tree(url):
    r = session.get(url)
    return html.fromstring(r.text)


def get_states():
    tree = get_tree(
        "http://www.amway.com.cn/content/china/accl/amwaychina/zh_cn/about/ztchome.html"
    )
    return tree.xpath(
        "//div[@class='list parbase section']/ul/li[contains(@class, 'list')]//a/@href"
    )


def get_urls():
    urls = []
    for state in get_states():
        tree = get_tree(f"http://www.amway.com.cn{state}")
        urls += tree.xpath("//a[@class='ztc-shop-link']/@href")

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"http://www.amway.com.cn{slug}"
    tree = get_tree(page_url)
    location_name = "".join(
        tree.xpath("//div[@class='shoplivecopy']/strong/text()")
    ).strip()
    line = tree.xpath("//div[@class='shopdetaillivecopy']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    raw_address = SgRecord.MISSING
    phone = SgRecord.MISSING
    hours_of_operation = SgRecord.MISSING
    postal = SgRecord.MISSING
    for l in line:
        if "址：" in l:
            raw_address = l.split("址：")[-1].strip()
        if "邮编：" in l:
            postal = l.split("邮编：")[-1].strip()
        if "店铺电话：" in l:
            phone = l.split("店铺电话：")[-1].strip()
        if "营业时间：" in l:
            hours_of_operation = l.split("营业时间：")[-1].strip()

    street_address, city, state, postal = get_international(raw_address, postal)
    text = "".join(tree.xpath("//meta[@name='location']/@content"))
    try:
        latitude, longitude = text.split("=")[-1].split(",")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="CN",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "http://www.amway.com.cn/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
