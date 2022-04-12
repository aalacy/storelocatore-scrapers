from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.gr"
    api_url = "https://johnsonfitness.gr/%ce%ba%ce%b1%cf%84%ce%b1%cf%83%cf%84%ce%ae%ce%bc%ce%b1%cf%84%ce%b1/#1596714377720-c5918c18-b3de"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h4/a[./span]")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://johnsonfitness.gr/%ce%ba%ce%b1%cf%84%ce%b1%cf%83%cf%84%ce%ae%ce%bc%ce%b1%cf%84%ce%b1/{slug}"
        location_name = "".join(d.xpath(".//span/text()"))
        ad = "".join(d.xpath(".//following::p[1]//text()")).replace("\n", "").strip()
        if location_name == "ΚΕΝΤΡΙΚΑ ΓΡΑΦΕΙΑ ΑΘΗΝΑΣ":
            ad = (
                "".join(d.xpath(".//following::p[2]//text()")).replace("\n", "").strip()
            )
        if location_name == "ΚΑΤΑΣΤΗΜΑ ΘΕΣΣΑΛΟΝΙΚΗΣ":
            ad = (
                "".join(d.xpath(".//following::p[2]//text()"))
                .replace("\n", "")
                .replace("Διεύθυνση:", "")
                .strip()
            )
        street_address = ad.split(",")[0].strip()
        postal = ad.split("TK")[1].split(",")[0].replace(":", "").strip()
        country_code = "GR"
        city = ad.split(",")[-1].strip()
        phone = (
            "".join(d.xpath('.//following::p[contains(text(), "Τηλ.")][1]/text()[1]'))
            .replace("Τηλ.", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"
        if location_name.find("ΘΕΣΣΑΛΟΝΙΚΗΣ") != -1:
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/following::p[text()="Ωράριο καταστήματος:"]/following-sibling::p/text()'
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
            state=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
