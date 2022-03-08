from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mcgrathsfishhouse.com/"
    page_url = "https://www.mcgrathsfishhouse.com/Contact-Us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/img]")
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        street_address = "".join(
            d.xpath(
                './/div[@class="rp-store-info-container rp-store-info-container-center"]/div/div[1]//text()'
            )
        )
        ad = "".join(
            d.xpath(
                './/div[@class="rp-store-info-container rp-store-info-container-center"]/div/div[2]//text()'
            )
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="rp-store-info-container rp-store-info-container-center"]/div/div[3]//text()'
                )
            )
            .replace("Phone:", "")
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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
