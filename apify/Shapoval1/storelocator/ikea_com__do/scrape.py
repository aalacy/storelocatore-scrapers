from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com.do/"
    api_url = "https://www.ikea.com.do/en/information/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/iframe]")
    for d in div:

        page_url = "https://www.ikea.com.do/en/information/contact"
        location_name = "".join(d.xpath(".//preceding::h3[1]/text()"))
        if location_name.find("Pick up") != -1:
            continue
        ad = (
            " ".join(
                d.xpath(
                    './/preceding::strong[text()="Address:"][1]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .replace("República Dominicana", "")
            .strip()
        )
        street_address = " ".join(ad.split(",")[:-2]).strip()
        street_address = " ".join(street_address.split())
        country_code = "Dominican Republic"
        city = ad.split(",")[-1].strip()
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                d.xpath(
                    './/preceding::strong[contains(text(), "Phone number")][1]/following-sibling::text()'
                )
            )
            .replace(" IKEA", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/preceding::div[./p[@class="txtHorarios mb-2 mb-md-1"]][2]/p[1]//text()'
                )
            )
            .replace("\n", " ")
            .replace("Shop:", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
