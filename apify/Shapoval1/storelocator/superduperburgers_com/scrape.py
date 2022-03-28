from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.superduperburgers.com"
    api_url = "https://www.superduperburgers.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-6"]')
    for d in div:

        page_url = "https://www.superduperburgers.com/locations/"
        location_name = "".join(d.xpath(".//h3//text()"))
        delivery = "".join(d.xpath('.//strong[text()="*DELIVERY ONLY*"]/text()'))
        if delivery or location_name.find("Coming Soon") != -1:
            continue
        ad = (
            "".join(d.xpath(".//h3/following-sibling::p//text()"))
            .replace("(Directions)", "")
            .strip()
        )
        if ad.find("Pickup Order") != -1:
            ad = ad.split("Pickup Order")[1].strip()
        if ad.find("Delivery") != -1:
            ad = ad.split("Delivery")[1].strip()
        if ad.find("  ") != -1:
            ad = ad.split("  ")[0].strip()
        if ad.find("Daily") != -1:
            ad = ad.split("Daily")[0].strip()
        street_address = " ".join(ad.split(",")[:-2]).strip()
        street_address = " ".join(street_address.split())
        state = ad.split(",")[-1].split()[0].strip()
        postal = ad.split(",")[-1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[-2].strip()
        phone = "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//p[contains(text(), 'pm')]//text()"))
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
