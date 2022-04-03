from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.lv/"
    api_url = "https://cars.honda.lv/dealer-search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./a[contains(@href, "mailto")]]')
    for d in div:
        info = " ".join(d.xpath(".//text()")).replace("\n", "").strip()
        page_url = "https://cars.honda.lv/dealer-search"
        location_name = (
            "".join(d.xpath(".//preceding-sibling::h2/text()"))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        if "serviss" in location_name:
            location_type = "service"
        ad = info.split("  ")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode.replace("LV-", "").strip() or "<MISSING>"
        country_code = "LV"
        city = a.city or "<MISSING>"
        if "Berģi" in location_name:
            city = "Berģi"
        phone = info.split("  ")[-3].split("Tālr.:")[1].split("E")[0].strip()
        hours_of_operation = info.split("  ")[1].strip()
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Autosalons:") != -1:
            hours_of_operation = hours_of_operation.split("Autosalons:")[1].strip()
        if hours_of_operation.find("tirdzniecība:") != -1:
            hours_of_operation = hours_of_operation.split("tirdzniecība:")[1].strip()

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
