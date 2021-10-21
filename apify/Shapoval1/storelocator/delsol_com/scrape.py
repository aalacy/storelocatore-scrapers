from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.delsol.com/"
    api_url = "https://www.delsol.com/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="region-list"]/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        country_code = (
            "".join(d.xpath(".//preceding::h3[1]/text()"))
            .replace("WESTERN", "")
            .replace("EASTERN", "")
            .strip()
        )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="page-heading"]/text()')) or "<MISSING>"
        )
        ad = (
            " ".join(tree.xpath('//*[text()="Address"]/following-sibling::p[1]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address.find("This Store Is") != -1:
            street_address = street_address.split("This Store Is ")[0].strip()
        if street_address == "100":
            street_address = "100 Fortaleza"
        if street_address == "#26":
            street_address = "#26 Duty Free Point"

        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name.split(",")[1].strip()
        latitude = "".join(tree.xpath("//div/@data-latitude")) or "<MISSING>"
        longitude = "".join(tree.xpath("//div/@data-longitude")) or "<MISSING>"
        phone = (
            "".join(tree.xpath('//*[text()="Contact"]/following-sibling::a[1]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//tr[@class="hours-row"]/td/text()'))
            .replace("\n", "")
            .replace("Open when ships are in port", "")
            .strip()
            or "<MISSING>"
        )
        if (
            hours_of_operation.find("When ships port") != -1
            or hours_of_operation.find("When ships are in port") != -1
        ):
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Open May to September") != -1:
            hours_of_operation = "Closed"

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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
