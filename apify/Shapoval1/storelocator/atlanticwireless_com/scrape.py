from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "http://www.atlanticwireless.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "Google Maps")]')
    for d in div:

        page_url = "http://www.atlanticwireless.com/store-locator/"
        location_name = (
            "".join(d.xpath(".//preceding-sibling::strong//text()"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = "".join(d.xpath(".//preceding::strong[1]//text()"))
        street_address = (
            "".join(d.xpath(".//preceding-sibling::text()[4]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = (
                "".join(d.xpath(".//text()[2]"))
                .replace("\n", "")
                .replace("NC,", "NC")
                .strip()
            )

        czp = (
            "".join(d.xpath(".//preceding-sibling::text()[3]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if czp == "<MISSING>":
            czp = (
                "".join(d.xpath(".//text()[3]"))
                .replace("\n", "")
                .replace("NC,", "NC")
                .replace("Greenville NC 27833", "Greenville, NC 27833")
                .strip()
            )

        state = czp.split(",")[1].split()[0].strip()
        postal = czp.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = czp.split(",")[0].strip()
        text = "".join(d.xpath(".//@href")) or "<MISSING>"
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
            "".join(d.xpath(".//preceding-sibling::text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if phone.find("Corporate Mailing Address") != -1:
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//following-sibling::text()"))
            .replace("\n", "")
            .replace("Hours:", "")
            .strip()
            or "<MISSING>"
        )
        if street_address.find("17230") != -1:
            hours_of_operation = (
                hours_of_operation
                + " "
                + "".join(d.xpath(".//following::p[1]/text()"))
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
    locator_domain = "http://www.atlanticwireless.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
