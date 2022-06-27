from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.colemangroup.co.uk/"
    api_url = "https://www.colemangroup.co.uk/store-finder/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//select[@class="store-select__dropdown"]/option[contains(@value, "/store")]'
    )
    for d in div:
        slug = "".join(d.xpath(".//@value"))
        page_url = f"https://www.colemangroup.co.uk{slug}"
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "Contact")]/preceding-sibling::p[3]/text()'
                )
            )
            or "<MISSING>"
        )
        state = "<MISSING>"
        postal = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "Contact")]/preceding-sibling::p[1]/text()'
                )
            )
            or "<MISSING>"
        )
        country_code = "UK"
        city = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "Contact")]/preceding-sibling::p[2]/text()'
                )
            )
            or "<MISSING>"
        )
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//p[contains(text(), "Tel No.")]//a//text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./div/h2[contains(text(), "Opening times")]]//text() | //div[./div/div/h2/span[text()="Opening times"]]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("Opening times", "").strip()
            or "<MISSING>"
        )
        per_cls = "".join(
            tree.xpath('//h2[contains(text(), "permanently closed")]/text()')
        )
        if per_cls:
            continue

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
