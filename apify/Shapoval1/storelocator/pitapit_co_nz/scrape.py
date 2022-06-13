from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pitapit.co.nz"
    api_url = "https://www.pitapit.co.nz/store-locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "location_l ")]')
    for d in div:

        page_url = "https://www.pitapit.co.nz/store-locator"
        location_name = "".join(d.xpath('.//div[@class="loc_item"]/h6[1]/text()'))
        ad = "".join(d.xpath('.//div[@class="text_part"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NZ"
        city = a.city or "<MISSING>"
        if city.count(" ") == 2:
            city = city.split()[-1].strip()
        if street_address.find("0230") != -1:
            street_address = street_address.replace("0230", "").strip()
            postal = "0230"
        if street_address.find("Auckland") != -1:
            street_address = street_address.replace("Auckland", "").strip()
            city = "Auckland"
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        if phone.find("OR") != -1:
            phone = phone.split("OR")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//button[@class="read-more"]/preceding::p[1]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        tmp_cls = "".join(
            d.xpath(
                './/h6[text()="Temporarily closed."]/text() | .//h6[contains(text(), "Temporarily closed")]/text()'
            )
        )
        if tmp_cls:
            hours_of_operation = "Temporarily closed"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    d.xpath('.//button[@class="read-more"]/preceding::p[2]/text()')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation == "(OPERATING HOURS MAY DIFFER)":
            hours_of_operation = "<MISSING>"
        if street_address.find("23 Jean Archie Drive") != -1:
            hours_of_operation = (
                " ".join(
                    d.xpath('.//button[@class="read-more"]/preceding::p[2]/text()')
                )
                .replace("\n", "")
                .strip()
                + " "
                + hours_of_operation
            )
        if hours_of_operation.find("Holidays") != -1:
            hours_of_operation = hours_of_operation.split("Holidays")[0].strip()

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
