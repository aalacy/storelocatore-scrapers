from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://eastcoastwarehouse.com/"
    api_url = "https://eastcoastwarehouse.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h1/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//section[@class="content-section"]//h2')
        for d in div:

            location_name = "".join(d.xpath(".//text()")).strip()
            if location_name == "Facility Information":
                continue
            street_address = (
                "".join(d.xpath("./following-sibling::p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(d.xpath("./following-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            info = d.xpath("./following-sibling::p[1]//text()")
            info = list(filter(None, [a.strip() for a in info]))
            phone = "<MISSING>"
            for i in info:
                if "Phone:" in i:
                    phone = str(i).replace("Phone:", "").strip()
            if phone == "TBD":
                phone = "<MISSING>"
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        './/following::h2[./strong[contains(text(), "Facility Information")]]/following-sibling::ul[1]/li[1]/text()[1] | .//following::h2[contains(text(), "Facility Information")]/following-sibling::ul[1]/li[1]/text()[1]'
                    )
                )
                .replace("*", "")
                .replace("\n", "")
                .strip()
            )
            if street_address == "202 Port Jersey Boulevard" and tree.xpath(
                '//li[contains(text(), "202 Port Jersey Blvd Location is open until 6:00pm")]/text()'
            ):
                hours_of_operation = "Monday-Friday 8:00am-6:00pm"

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
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
