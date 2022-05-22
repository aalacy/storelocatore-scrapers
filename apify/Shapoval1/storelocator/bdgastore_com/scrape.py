from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bdgastore.com/"
    api_url = "https://bdgastore.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "Store")]')
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://bdgastore.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()"))
        ad = (
            "".join(
                tree.xpath(
                    '//strong[text()="We are hidden in plain sight  at "]/following-sibling::strong/text()'
                )
            ).replace("@ ROW DTLA", "")
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                "".join(
                    tree.xpath(
                        '//strong[contains(text(), "We are hidden in plain sight at")]/text()'
                    )
                )
                .split("We are hidden in plain sight at")[1]
                .strip()
            )
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong/span[text()="Store Hours"]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
