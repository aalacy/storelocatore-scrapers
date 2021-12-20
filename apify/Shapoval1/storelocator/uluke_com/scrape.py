from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://uluke.com"
    api_url = "http://uluke.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="x-acc-content"]//*[text()="Directions"]')
    for d in div:
        info = " ".join(d.xpath(".//preceding::p[1]//text()")).replace("\n", "").strip()
        ad = info
        ad = (
            " ".join(ad.split())
            .replace("Hours :", "Hours:")
            .replace("Luke Gas Station", "")
            .replace("BP", "")
            .replace("OPEN 24 Hours", "")
            .replace("6259 Melton Rd.", "6259 Melton Rd.,")
            .strip()
        )
        if ad.find("|") != -1:
            ad = ad.split("|")[1].strip()
        info = " ".join(info.split()).replace("Hours :", "Hours:")
        if ad.find("Hours:") != -1:
            ad = ad.split("Hours:")[0].strip()
        if ad.find("Phone:") != -1:
            ad = ad.split("Phone:")[0].strip()
        page_url = "http://uluke.com/locations/"
        location_name = info.split("|")[0].strip()
        street_address = ad.split(",")[0].strip()
        state = (
            "".join(d.xpath('.//preceding::span[@class="x-acc-header-text"][1]/text()'))
            .split(",")[1]
            .strip()
        )
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = (
            info.split("|")[0].replace("STORE", "").replace("Store", "").strip()
        )
        jsblock = "".join(tree.xpath("//div/@data-x-params"))
        latitude = (
            jsblock.split(f"Store {store_number}")[0]
            .split('"lat":"')[-1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            jsblock.split(f"Store {store_number}")[0]
            .split('"lng":"')[-1]
            .split('"')[0]
            .strip()
        )
        phone = "<MISSING>"
        if info.find("Phone:") != -1:
            phone = info.split("Phone:")[1].strip()
        hours_of_operation = "<MISSING>"
        if info.find("Hours:") != -1:
            hours_of_operation = info.split("Hours:")[1].strip()

        if hours_of_operation.find("Phone") != -1:
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("Luke Car Wash", "").replace("|", "").strip()
        )
        if info.find("OPEN 24 Hours") != -1:
            hours_of_operation = "OPEN 24 Hours"
        if phone.find("OPEN 24 Hours") != -1:
            phone = phone.replace("OPEN 24 Hours", "").strip()
            hours_of_operation = "OPEN 24 Hours"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
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
