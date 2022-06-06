from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pinkies.com/"
    page_url = "https://pinkies.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Get Directions"]')
    for d in div:

        location_name = "".join(d.xpath(".//preceding::h2[1]//text()"))
        street_address = (
            "".join(d.xpath(".//preceding::text()[5]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if street_address.find("(") != -1 or street_address == "<MISSING>":
            street_address = (
                "".join(d.xpath(".//preceding::text()[6]")).replace("\n", "").strip()
                or "<MISSING>"
            )
        if street_address == "<MISSING>":
            street_address = (
                "".join(d.xpath(".//preceding::text()[4]")).replace("\n", "").strip()
                or "<MISSING>"
            )
        ad = (
            "".join(d.xpath(".//preceding::text()[4]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if ad.find(",") == -1:
            ad = (
                "".join(d.xpath(".//preceding::text()[3]")).replace("\n", "").strip()
                or "<MISSING>"
            )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = "".join(d.xpath(".//preceding::text()[3]")).replace("\n", "").strip()
        if phone.find("(") == -1:
            phone = (
                "".join(d.xpath(".//preceding::text()[2]")).replace("\n", "").strip()
            )
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/preceding::h2[./strong[contains(text(), "WE’RE OPEN")]]/strong/text()'
                )
            )
            .replace("\n", "")
            .replace("WE’RE OPEN", "")
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
