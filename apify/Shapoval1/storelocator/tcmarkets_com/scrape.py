import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tcmarkets.com/"
    api_url = "https://tcmarkets.com/store-finder/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="pp-photo-content-inner"]/a[./img]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = tree.xpath('//div[@class="fl-rich-text"]//text()')
        info = list(filter(None, [a.strip() for a in info]))
        ad_info = " ".join(info)
        if ad_info.find("Store Address") != -1:
            ad_info = ad_info.split("Store Address")[1].strip()
        if ad_info.find("Store Hours") != -1:
            ad_info = ad_info.split("Store Hours")[0].strip()
        if ad_info.find("Find a Store") != -1:
            continue
        ph = re.findall(r"[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}", ad_info) or "<MISSING>"
        phone = "".join(ph[0]) or "<MISSING>"
        if ad_info.find(f"{phone}") != -1:
            ad_info = ad_info.split(f"{phone}")[0].strip()
        location_name = (
            "".join(tree.xpath("//h6//text() | //h2//text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[@style="color: #ff0000; font-size: 16px;"]]//text()'
                    )
                )
                .replace("\r\n", "")
                .strip()
                or "<MISSING>"
            )
        a = parse_address(International_Parser(), ad_info)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if phone == "<":
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//p[./strong[text()="Store Hours:"]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = (
                "Monday" + " " + hours_of_operation.split("Monday")[1].strip()
            )
        cms = "".join(tree.xpath('//img[contains(@src, "coming-soon")]/@src'))
        if cms:
            hours_of_operation = "Coming Soon"

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
