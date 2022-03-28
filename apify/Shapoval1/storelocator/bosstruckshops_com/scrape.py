from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://bosstruckshops.com/page-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'locations/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://bosstruckshops.com/"
    page_url = "".join(url)
    if page_url.count("/") != 5:
        return

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    ad = tree.xpath('//a[contains(text(), "DIRECTIONS")]/following::div[1]//text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    adr = "".join(ad[0]).strip()
    a = parse_address(USA_Best_Parser(), adr)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "US"
    city = a.city or "<MISSING>"
    if city == "<MISSING>":
        street_address = " ".join(adr.split(",")[0].split()[:-1])
        city = adr.split(",")[0].split()[-1].strip()
        state = adr.split(",")[1].strip()
        postal = adr.split(",")[-1].strip()

    location_name = (
        " ".join(
            tree.xpath('//a[contains(text(), "DIRECTIONS")]/preceding::h3[1]//text()')
        )
        .replace("\n", "")
        .strip()
    )
    phone = (
        "".join(tree.xpath('//a[contains(@href, "tel")]/@href'))
        .replace("tel:", "")
        .strip()
    )
    text = "".join(tree.xpath('//a[contains(text(), "DIRECTIONS")]/@href'))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    tmp = []
    hours_of_operation = "<MISSING>"
    for i in ad:
        if "Mon" in i or "Fri" in i or "Sat" in i or "Sun" in i:
            tmp.append(i)
        hours_of_operation = "; ".join(tmp).replace("\n", "").replace("\r", "").strip()

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=adr,
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
