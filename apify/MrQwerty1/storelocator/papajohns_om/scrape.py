from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    urls = []
    data = {"citycode": "1"}
    r = session.post(
        "http://papajohns.om/oman/users/ajax_login/searchloadblocks/1/", data=data
    )
    tree = html.fromstring(r.text)
    ids = tree.xpath("//option/@value")
    for _id in ids:
        if _id == "0":
            continue
        urls.append(
            f"http://papajohns.om/oman/users/getlocation/getlocationdeatails/0/{_id}"
        )

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//p[@class='head']/text()")).strip()
    if not location_name:
        return
    line = tree.xpath("//div[@class='full_width']/p[1]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    city = line.pop().replace(",", "").replace(".", "")
    phone = line.pop().replace(",", "")
    street_address = ", ".join(line).strip()
    if street_address.endswith(","):
        street_address = street_address[:-1].strip()
    store_number = page_url.split("/")[-1]

    try:
        latitude = tree.xpath("//marker/@lat")[0]
        longitude = tree.xpath("//marker/@lng")[0]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours_of_operation = (
        tree.xpath(
            "//p[./strong[contains(text(), 'Hours')]]/following-sibling::p/text()"
        )[0]
        .replace("Carryout:", "")
        .strip()
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        country_code="OM",
        store_number=store_number,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "http://papajohns.om/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
