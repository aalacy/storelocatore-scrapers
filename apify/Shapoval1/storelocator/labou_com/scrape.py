from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.labou.com/"
    page_url = "https://www.labou.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/div/div/h3]")
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        ad = "".join(d.xpath(".//h3/following::p[1]//text()")).strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone: ")]/strong[1]//text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[./span/strong[contains(text(), "Hours of operation")]]//text()'
                )
            )
            .replace("\n", "")
            .replace("Hours of operation:", "")
            .replace("Hours of operation", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.startswith(":"):
            hours_of_operation = "".join(hours_of_operation[1:]).strip()
        text = "".join(d.xpath(".//h3//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
