from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.talktimestore.com"
    api_url = "https://www.talktimestore.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[.//span[contains(text(), "Ph:")]]]')
    for d in div:
        info = d.xpath(".//text()")
        info = list(filter(None, [a.strip() for a in info]))
        page_url = (
            "".join(
                d.xpath(
                    './/following::div[.//span[text()="Store Details"]][1]//a/@href'
                )
            )
            or "https://www.talktimestore.com/locations"
        )
        location_name = (
            "".join(d.xpath(".//preceding::h2[1]//text()")).replace("\n", "").strip()
        )
        ad = " ".join(info).split("Ph")[0].strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = "".join(info).split("Ph:")[1].strip() or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url != "https://www.talktimestore.com/locations":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./h2[./span[text()="Opening Hours"]]]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
