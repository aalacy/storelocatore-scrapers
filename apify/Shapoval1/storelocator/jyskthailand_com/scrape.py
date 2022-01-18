from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jyskthailand.com"
    api_url = "https://www.jyskthailand.com/dealerlocator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="store-item"]')
    for d in div:

        page_url = "https://www.jyskthailand.com/dealerlocator/"
        location_name = "".join(d.xpath('.//input[@name="dealer-title"]/@value'))
        ad = (
            " ".join(d.xpath('.//input[@name="dealer-address"]/@value'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Thailand"
        city = a.city or "<MISSING>"
        latitude = "".join(
            d.xpath('.//input[contains(@id, "dealer_latitude_")]/@value')
        )
        longitude = "".join(
            d.xpath('.//input[contains(@id, "dealer_longitude_")]/@value')
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="store-info"]/p[2]//text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Google map") != -1:
            hours_of_operation = hours_of_operation.split("Google map")[1].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[1].split(")")[0].strip()

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
