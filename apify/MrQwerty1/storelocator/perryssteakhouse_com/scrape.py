from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://perryssteakhouse.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(@class, 'loc-spacer')]/@href"))


def get_friendswood(sgw: SgWriter):
    page_url = "https://perryandsonsmarketandgrille.com/locations_category/friendswood"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath("//div[@class='col-md-4 col-sm-5']/h3/text()")
    ).strip()
    line = tree.xpath(
        "//p[./a[contains(@href, 'google')]]/preceding-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    phone = line.pop()
    street_address = line.pop(0)
    line = line.pop()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]

    text = "".join(tree.xpath("//p[./a[contains(@href, 'google')]]/a/@href"))
    latitude = text.split("sll=")[1].split(",")[0]
    longitude = text.split("sll=")[1].split(",")[1].split("&")[0]
    hours = tree.xpath("//div[@class='taxonomy-description']/p[last()]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "<MISSING>"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='lockup']/h3/text()")).strip()
    line = tree.xpath(
        "//div[@class='info']//span[@class='vertical'][1]/following-sibling::span/p[1]/text()"
    )
    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = (
        "".join(
            tree.xpath("//div[@class='info']//a[contains(@href, 'tel')]/text()")
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lng]/@data-lng"))

    _tmp = []
    hours = tree.xpath("//div[@class='info']//p[@class='dine-in']")
    for h in hours:
        inter = h.xpath(".//text()")
        inter = list(filter(None, [i.strip() for i in inter]))
        day = inter.pop(0)
        time = inter.pop()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if phone == "<MISSING>" and hours_of_operation == "<MISSING>":
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    get_friendswood(sgw)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://perryssteakhouse.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
