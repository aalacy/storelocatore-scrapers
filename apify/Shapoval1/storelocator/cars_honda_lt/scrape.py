from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cars.honda.lt/"
    page_url = "https://cars.honda.lt/dealer-search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="imageWithContentCroppedContent"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        info = " ".join(d.xpath(".//p/text()")).replace("\n", "").strip()
        info = " ".join(info.split())
        ad = info
        if ad.find("Automobilių servisas:") != -1:
            ad = ad.split("Automobilių servisas:")[0].strip()
        if ad.find("Darbo laikas:") != -1:
            ad = ad.split("Darbo laikas:")[0].strip()

        location_type = "<MISSING>"
        if location_name.find("service") != -1:
            location_type = "service"
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode.replace("LT-", "").strip() or "<MISSING>"
        country_code = "LT"
        city = "".join(d.xpath(".//h2/text()"))
        if city.find("service") != -1:
            location_type = "service"
        if city.find(".") != -1:
            city = city.split(".")[1].split()[0].strip()

        phone = info.split("Informacija:")[1].strip()
        if phone.find("El. paštas:") != -1:
            phone = phone.split("El. paštas:")[0].strip()
        if phone.find("Automobilių") != -1:
            phone = phone.split("Automobilių")[0].strip()
        phone = phone.replace("Tel.", "").replace(":", "").replace("nr.", "").strip()
        if phone.count("(") == 2:
            phone = "(" + phone.split("(")[1]
        hours_of_operation = info.split("Automobilių")[1].strip()
        if hours_of_operation.find("Informacija") != -1:
            hours_of_operation = (
                hours_of_operation.split("Informacija")[0].replace(". ", "").strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("salonas", "").replace("servisas:", "").strip()
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
