from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dkny.com/"
    for i in range(1, 500):
        page_url = f"https://www.dkny.com/store-locator/{i}/"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            continue
        location_name = "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
        ad = (
            "".join(tree.xpath("//h1/following-sibling::div[1]/p[1]//text()"))
            .replace("\n", "")
            .strip()
        )

        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = ad
        if postal.find(",") != -1:
            postal = ad.split(",")[-1].strip()
        country_code = "<MISSING>"
        city = "<MISSING>"
        if ad.find(",") != -1:
            city = ad.split(",")[0].strip()
        store_number = page_url.split("/")[-2].strip()
        text = "".join(tree.xpath('//a[contains(text(), "Get Directions")]/@href'))
        try:
            latitude = text.split("daddr=")[1].split(",")[0].strip()
            longitude = text.split("daddr=")[1].split(",")[1].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="schedule-list"]//ul//li//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if (
            hours_of_operation.find(
                "Monday - Tuesday - Wednesday - Thursday - Friday - Saturday - Sunday -"
            )
            != -1
        ):
            hours_of_operation = "<MISSING>"

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
