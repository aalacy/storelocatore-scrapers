from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://purrfectautoservice.com/"
    page_url = "https://purrfectautoservice.com/california.htm"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div_1 = tree.xpath("//p[./iframe]")
    for v in div_1:

        location_name = "".join(v.xpath(".//preceding-sibling::h3[1]/text()"))
        ad = v.xpath(".//preceding-sibling::p[1]//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = (
            " ".join(v.xpath(".//preceding-sibling::p[1]//text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        adr = " ".join(adr.split())
        if adr.find("Phone") != -1:
            adr = adr.split("Phone")[0].strip()
        if adr.find("Address:") != -1:
            adr = adr.split("Address:")[1].strip()

        a = parse_address(USA_Best_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        store_number = location_name.split("#")[1].strip()
        text = "".join(v.xpath(".//following-sibling::p[1]//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = " ".join(ad).split("Phone:")[1].split()[0].strip()

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=adr,
        )

        sgw.write_row(row)

    locator_domain = "https://purrfectautoservice.com/"
    page_url = "https://purrfectautoservice.com/nevada.htm"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div_1 = tree.xpath("//iframe")
    for v in div_1:

        location_name = "".join(v.xpath(".//preceding::h3[1]/text()"))
        street_address = (
            "".join(
                v.xpath(
                    './/preceding::strong[text()="Phone:"][1]/preceding-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = (
                "".join(
                    v.xpath(
                        './/preceding::strong[text()="Phone:"][1]/preceding-sibling::span[2]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        ad = (
            "".join(
                v.xpath(
                    './/preceding::strong[text()="Phone:"][1]/preceding-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                "".join(
                    v.xpath(
                        './/preceding::strong[text()="Phone:"][1]/preceding-sibling::span[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = location_name.split("#")[1].strip()
        text = "".join(v.xpath('.//following::a[contains(@href, "maps")][1]/@href'))
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
            "".join(
                v.xpath(
                    './/preceding::strong[text()="Phone:"][1]/following-sibling::a[contains(@href, "tel")][1]/text()'
                )
            )
            .replace("\n", "")
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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
