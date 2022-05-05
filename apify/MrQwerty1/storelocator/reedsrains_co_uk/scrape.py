from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.reedsrains.co.uk/branches")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='branch-thumbnail__link']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.reedsrains.co.uk{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//div[@class='branch-details__address']/text()")
    line = list(filter(None, [l.replace(",", "").strip() for l in line]))
    location_name = line.pop(0)
    raw_address = " ".join(line)
    if line[0][0].isalpha() and line[1][0].isdigit():
        street_address = line[1]
        line = line[2:]
    else:
        street_address = line.pop(0)
    postal = line.pop()
    city = line.pop()
    phone = "".join(
        tree.xpath(
            "//div[@class='branch-details__contact-details branch-details__contact-details--phone']//span/text()"
        )
    ).strip()
    if "(" in phone:
        phone = phone.split("(")[0].strip()

    try:
        source = "".join(tree.xpath("//img[contains(@src, 'center=')]/@src"))
        latitude, longitude = source.split("&center=")[1].split("&")[0].split(",")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//span[@class='opening-time-wrap']")
    for h in hours:
        day = "".join(h.xpath("./span/text()")).strip()
        inter = "".join(h.xpath("./text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.reedsrains.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
