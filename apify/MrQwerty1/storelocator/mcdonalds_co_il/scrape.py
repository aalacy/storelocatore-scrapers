from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get(
        "https://www.mcdonalds.co.il/%D7%90%D7%99%D7%AA%D7%95%D7%A8_%D7%9E%D7%A1%D7%A2%D7%93%D7%94"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='position_r overflow_h show focNo']/@href")


def get_data(page_url, sgw: SgWriter):
    page_url = f"https:{page_url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    store_number = page_url.split("=")[-1]
    location_name = "".join(
        tree.xpath("//div[@class='page_title padding_hf_h ']//h1/text()")
    ).strip()
    line = tree.xpath(
        "//div[@class='page_title padding_hf_h ']//h1/text()|//div[@class='page_title padding_hf_h ']//h2//text()"
    )
    raw_address = ", ".join(list(filter(None, [l.strip() for l in line])))
    street_address, city, state, postal = get_international(raw_address)

    phone = "".join(
        tree.xpath("//div[@class='padding_hf_h']//a[contains(@href, 'tel:')]/text()")
    ).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        latitude = text.split("lat=")[1].split("&")[0]
        longitude = text.split("lon=")[1].split("&")[0]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    try:
        hours = tree.xpath("//div[@class='inline padding_v padding_hf_h']")[0]
        days = hours.xpath(".//div[@class='inline w_25']/span/text()")
        inters = hours.xpath(".//div[@class='inline w_75']/text()")
        _tmp.append("".join(hours.xpath(".//span[@class='h_color']/text()")).strip())
        for d, i in zip(days, inters):
            _tmp.append(f"{d}: {i}")
    except:
        pass

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="IL",
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.mcdonalds.co.il/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
