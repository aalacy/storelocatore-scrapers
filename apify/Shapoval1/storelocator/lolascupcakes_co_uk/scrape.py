from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lolascupcakes.co.uk/"
    page_url = "https://www.lolascupcakes.co.uk/stores.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="singlestore"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "<MISSING>"
        if "Locker" in location_name:
            location_type = "Collection Locker"
        ad = (
            "".join(d.xpath('.//span[contains(@id, "Address1")]/text()'))
            .replace("\n", "")
            .strip()
            + " "
            + "".join(d.xpath('.//span[contains(@id, "Address2")]/text()'))
            .replace("\n", "")
            .strip()
        )
        street_lst = ad.split()
        tmp = []
        for s in street_lst:
            if "(" in s or ")" in s:
                continue
            tmp.append(s)
        street_address = " ".join(tmp).replace("St,", "St").strip()
        state = "<MISSING>"
        cp = (
            "".join(d.xpath('.//span[contains(@id, "PostCode")]/text()'))
            .replace("\n", "")
            .strip()
        )
        postal = cp.split(",")[0].strip()
        country_code = "UK"
        city = cp.split(",")[1].strip()
        phone = (
            "".join(d.xpath('.//div[contains(@id, "Phone")]//text()'))
            .replace("\n", "")
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="half last"]/p/text()'))
            .replace("\n", "")
            .replace("::", ":")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Bank") != -1:
            hours_of_operation = hours_of_operation.split("Bank")[0].strip()
        if hours_of_operation.find("Phone") != -1:
            phone = hours_of_operation.split("Phone:")[1].strip()
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()
        if hours_of_operation.find("Order") != -1:
            hours_of_operation = hours_of_operation.split("Order")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
