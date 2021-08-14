from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://tcmarkets.com/store-finder/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="pp-photo-content-inner"]/a[./img]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath("//h6//text() | //h2//text()")) or "<MISSING>"
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
        if location_name == "<MISSING>":
            continue
        if page_url == "https://tcmarkets.com/store-finder/mountain-home/":
            location_name = "TOWN AND COUNTRY DISCOUNT FOODS MOUNTAIN HOME, AR, 72653"
        street_address = (
            "".join(
                tree.xpath('//p[./strong[contains(text(), "Store Address")]]/text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath('//p[./strong[contains(text(), "Store Address")]]/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        if street_address.find("7278 E. Highway 14") != -1:
            ad = (
                "".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Store Address")]]/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        ad = ad.replace("Salem MO, 65560", "Salem, MO 65560")
        state = ad.split(",")[1].split()[0].strip()
        try:
            postal = ad.split(",")[1].split()[1].strip()
        except:
            postal = "<MISSING>"
        country_code = "USA"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(
                tree.xpath('//p[./strong[contains(text(), "Store Address")]]/text()[3]')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Store Address")]]/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if street_address.find("7278 E. Highway 14") != -1:
            phone = (
                "".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Store Address")]]/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(tree.xpath('//p[./strong[text()="Store Hours:"]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = (
                "Monday" + " " + hours_of_operation.split("Monday")[1].strip()
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
    locator_domain = "https://tcmarkets.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
