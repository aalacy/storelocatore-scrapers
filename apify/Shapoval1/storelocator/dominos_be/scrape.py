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
    r = session.get("https://www.dominos.be/sitemap.aspx", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/winkel/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.dominos.be/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    ad = (
        " ".join(tree.xpath('//span[@id="store-address-info"]//text()'))
        .replace("\n", "")
        .strip()
    )
    ad = " ".join(ad.split())
    street_address = ad.split(",")[0].strip()
    state = "<MISSING>"
    postal = ad.split(",")[1].split()[-1].strip()
    country_code = "BE"
    city = " ".join(ad.split(",")[1].split()[:-2]).strip()
    location_name = (
        "".join(tree.xpath('//h1[@class="storetitle"]/text()')) or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath('//div[@class="store-phone"]//text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[text()="Openingstijden"]/following-sibling::span/span[contains(@class, "trading")]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    latitude = "".join(tree.xpath('//input[@name="store-lat"]/@value')) or "<MISSING>"
    longitude = "".join(tree.xpath('//input[@name="store-lon"]/@value')) or "<MISSING>"
    try:
        store_number = "".join(page_url).split("-")[-1].strip()
    except:
        store_number = "<MISSING>"

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
        raw_address=ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
