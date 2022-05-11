from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.nationalselfstorage.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//*//text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.nationalselfstorage.com/"
    api_url = "".join(url)
    if api_url.find("index-by-state") == -1:
        return

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:
        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h2[@id="target-focus"]/text()')) or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                " ".join(
                    tree.xpath(
                        '//h2[@class="elementor-heading-title elementor-size-default"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="facility-address"]/text() | //div[contains(text(), "Dr.")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if location_name.find("Tucson") != -1:
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//span[./span[@class="ss-icon icon-ss-phone"]]/following-sibling::a//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//div[@id="inss_phone"]//*//text()'))
                .replace("\n", "")
                .strip()
            )
            phone = " ".join(phone.split())

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="gate-hours"]/div/div/text() | //strong[contains(text(), "ACCESS")]/text()'
                )
            )
            .replace("\n", "")
            .replace("ACCESS:", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="business-hours-row"]/div/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation.count("Open 24h") == 7:
            hours_of_operation = "Open 24h"
        ll = "".join(tree.xpath("//img/@data-src")) or "<MISSING>"
        try:
            latitude = ll.split("markers=")[1].split(",")[0].strip()
            longitude = ll.split("markers=")[1].split(",")[1].split("h")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            raw_address=ad,
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
