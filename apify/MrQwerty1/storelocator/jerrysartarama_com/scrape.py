from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.jerrysartarama.com/retail/store-index")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//h2[contains(text(), 'Affiliates')]/preceding-sibling::div[@class='rows']//a[@class='button']/@href"
    )


def get_data(page_url, sgw: SgWriter):
    if "?" in page_url:
        page_url = page_url.split("?")[0]

    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        if "@" not in text:
            latitude, longitude = text.split("dir/")[1].split("/")[0].split(",")
        else:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    if "wholesale" in str(r.url):
        location_type = "Wholesale"
        phone = "".join(
            tree.xpath("//footer//a[contains(@href, 'tel:')]/text()")
        ).strip()
        street_address = "".join(
            tree.xpath(
                "//footer//div[@class='street-address']/text()|//footer//div[@class='extended-address']/text()"
            )
        ).strip()
        city = "".join(tree.xpath("//footer//span[@class='locality']/text()")).strip()
        state = "".join(tree.xpath("//footer//span[@class='region']/text()")).strip()
        postal = "".join(
            tree.xpath("//footer//span[@class='postal-code']/text()")
        ).strip()
        location_name = f"{city}, {state}"

        lines = tree.xpath("//footer//p//text()")
        for line in lines:
            if not line.strip() or "Yes" in line:
                continue
            if ":" not in line:
                _tmp.append(f"{line.strip()};")
            else:
                _tmp.append(line.strip())
        hours_of_operation = "".join(_tmp)[:-1]
    else:
        location_type = "Retail"
        phone = "".join(tree.xpath("//span[@class='location-phone']//text()")).strip()
        location_name = "".join(
            tree.xpath("//span[@class='location-phone']/preceding-sibling::h2/text()")
        ).strip()
        line = tree.xpath("//h3[text()='Address:']/following-sibling::p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        csz = line.pop()
        street_address = ", ".join(line)
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[-1].strip()
        state, postal = csz.split()
        lines = tree.xpath(
            "//h3[contains(text(), 'Hours')]/following-sibling::p[1]//text()"
        )
        for line in lines:
            if not line.strip() or "Yes" in line:
                continue
            if ":" not in line:
                _tmp.append(f"{line.strip()};")
            else:
                _tmp.append(line.strip())
        hours_of_operation = "".join(_tmp)[:-1]

    if "retail" in page_url:
        location_type = "Retail"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
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
    locator_domain = "https://jerrysartarama.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
