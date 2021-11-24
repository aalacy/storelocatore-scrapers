from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://beyondjuiceryeatery.com/"
    api_url = "https://beyondjuiceryeatery.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./div[@class="one-loc-picture"]/img[not(contains(@src, "Coming-Soon"))]]'
    )
    for d in div:

        page_url = "https://beyondjuiceryeatery.com/locations/"
        location_name = "".join(d.xpath(".//h4/text()")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//h5/text()")).replace("\n", "").strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if location_name.find("Bloomfield Hills") != -1 and city == "<MISSING>":
            city = "Bloomfield Hills"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="one-loc-bottom"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if phone == "TEMPORARILY CLOSED":
            phone = "<MISSING>"
            hours_of_operation = "TEMPORARILY CLOSED"

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
