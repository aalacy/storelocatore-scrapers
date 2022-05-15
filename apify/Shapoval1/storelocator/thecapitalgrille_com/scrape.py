import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.thecapitalgrille.com/"
    api_url = "https://www.thecapitalgrille.com/locations-sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(
                tree.xpath(
                    '//input[@id="isLocationDetails"]/following-sibling::h1//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url.find("mexico") == -1 and page_url.find("costa-rica") == -1:
            street_address = (
                "".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .replace("Millenia Mall", "")
                .replace("Hynes Convention Ctr", "")
                .replace("Lasalle Plaza", "")
                .replace("City Centre Four", "")
                .strip()
            )
            ad = (
                "".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
            country_code = "US"
            phone = (
                "".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            text = "".join(tree.xpath('//img[@id="staticMapBoxImgUrl"]/@src'))
            latitude = text.split("(")[1].split(",")[1].split(")")[0].strip()
            longitude = text.split("(")[1].split(",")[0].strip()
            js_block = "".join(
                tree.xpath('//script[@type="application/ld+json"]/text()')
            )
            js = json.loads(js_block)
            hours_of_operation = " ".join(js.get("openingHours")) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(tree.xpath('//ul[@class="inline top-bar"]/li//text()'))
                    .replace("Today", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("None", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split())
            store_number = js.get("branchCode")
        if page_url.find("mexico") != -1:
            street_address = (
                " ".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[position() < 3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            country_code = "México"
            city = (
                "".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//b[contains(text(), "Phone")]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            text = "".join(tree.xpath('//img[@id="staticMapBoxImgUrl"]/@src'))
            latitude = text.split("(")[1].split(",")[1].split(")")[0].strip()
            longitude = text.split("(")[1].split(",")[0].strip()
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .split("Opening Hours")[1]
                .split("Phone")[0]
                .strip()
            )
        if page_url.find("costa-rica") != -1:
            street_address = (
                " ".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]/text()[position() < 4]'
                    )
                )
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
            city = "San José"
            country_code = "Costa Rica"
            phone = (
                "".join(
                    tree.xpath(
                        '//b[contains(text(), "Phone")]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            text = "".join(tree.xpath('//img[@id="staticMapBoxImgUrl"]/@src'))
            latitude = text.split("(")[1].split(",")[1].split(")")[0].strip()
            longitude = text.split("(")[1].split(",")[0].strip()
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//input[@id="isLocationDetails"]/following-sibling::h1/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .split("Hours")[1]
                .split("Phone")[0]
                .strip()
            )

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
