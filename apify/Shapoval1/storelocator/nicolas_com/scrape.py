import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    api_url = "https://www.nicolas.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//loc")
    tmp = []
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.content)
        try:
            block = tree.xpath("//url/loc")
        except:
            continue

        for b in block:
            pg_url = "".join(b.xpath(".//text()"))
            if "/magasins/" in pg_url:
                tmp.append(pg_url)
    return tmp


def get_data(url, sgw: SgWriter):
    locator_domain = "https://nicolas.com/"
    page_url = "".join(url)
    if page_url.find("/fr/") != -1:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    phone = (
        "".join(tree.xpath('//address/a[contains(@href, "tel")]/text()')) or "<MISSING>"
    )
    location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
    if location_name == "<MISSING>":
        return
    hours = tree.xpath('//div[@class="ns-StoreDetails-openingsTimesDetail"]')
    days = tree.xpath('//div[contains(@class, "ns-StoreDetails-openingsDay")]//text()')
    days = list(filter(None, [a.strip() for a in days]))
    tmp = []
    _tmp = []
    for h in hours:
        open = (
            "".join(
                h.xpath('./div[@class="ns-StoreDetails-openingsTimesDetailAM"]/text()')
            )
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )
        close = (
            "".join(
                h.xpath('./div[@class="ns-StoreDetails-openingsTimesDetailPM"]/text()')
            )
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )

        line = f"{open}-{close}"
        tmp.append(line)
    closed = (
        "".join(
            tree.xpath(
                '//div[@class="ns-StoreDetails-openingsTimesDetail ns-StoreDetails-openingsTimesDetail--closed"]/text()'
            )
        )
        .replace("\n", "")
        .replace("\t", "")
        .strip()
    )

    if (
        "".join(
            tree.xpath(
                '//div[@class="ns-StoreDetails-openingsTimes"]/div[contains(@class, "ns-StoreDetails-openingsTimesDetail ns-StoreDetails-openingsTimesDetail--closed")]/text()'
            )
        )
        .replace("\n", "")
        .replace("\t", "")
        .strip()
        == "Closed"
    ):
        tmp.append(closed)

    for d, t in zip(days, tmp):
        _tmp.append(f"{d.strip()}: {t.strip()}")
    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    hours_of_operation = " ".join(hours_of_operation.split())
    if closed.count("Closed") == 7:
        hours_of_operation = "Closed"
    if page_url == "https://www.nicolas.com/en/magasins/RENNES-NEMOURS/s/00008633.html":
        hours_of_operation = " ".join(days).replace("\n", "").strip()
        hours_of_operation = " ".join(hours_of_operation.split())

    jss = (
        "".join(tree.xpath("//div/@data-stores"))
        .replace('"CAVE JRC"', "'CAVE JRC'")
        .replace('"39 ', "'39 ")
    )
    try:
        js = json.loads(jss)
    except:
        return

    for j in js.values():

        street_address = j.get("address") or "<MISSING>"
        if street_address == "<MISSING>":
            street_address = (
                "".join(
                    tree.xpath('//address[@class="ns-StoreDetails-address"]/text()[2]')
                )
                .replace("\n", "")
                .strip()
            )
        city = j.get("town")
        state = "<MISSING>"
        postal = j.get("postcode")
        country_code = j.get("country")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("name")

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
