from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sglogging import sglog


def get_urls():
    urls = []
    r = session.get(
        "https://www.supermarches-en-belgique.com/sitemap.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 4 and not link.endswith("/"):
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        logger.info(f"{page_url}: {r}")
        return
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var dejafull;')]/text()"))
    tex = text.split('var html = "')
    tex.pop(0)
    logger.info(f"{page_url}: {len(tex)} records")

    for t in tex:
        source = t.split('";')[0]
        d = html.fromstring(source)
        line = d.xpath(".//text()")
        line = list(
            filter(None, [li.replace("Site Internet", "").strip() for li in line])
        )
        location_name = line.pop(0).replace("&#39;", "'")

        phone = SgRecord.MISSING
        if "tel." in line[-1].lower():
            phone = "".join(
                line.pop().lower().replace("tel", "").replace(".", "").split()
            )

        raw_address = ", ".join(line)
        zc = line.pop()
        postal = zc.split()[0]
        city = zc.replace(postal, "")
        if "(" in city:
            city = city.split("(")[0].strip()
        street_address = ", ".join(line).replace("&#39;", "'").replace(" -", "").strip()
        latitude = t.split("parseFloat(")[1].split("),")[0].strip()
        longitude = t.split("parseFloat(")[2].split("));")[0].strip()
        xpath = f"""//div[./b[contains(text(), "{location_name}")]]/img/@title"""
        try:
            location_type = tree.xpath(xpath)[0].replace("-", " ")
        except IndexError:
            location_type = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="BE",
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"{len(urls)} URLs to crawl...")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.supermarches-en-belgique.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="supermarches-en-belgique.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
