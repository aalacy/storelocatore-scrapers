from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://oldbootfactory.com/"
    page_url = "https://oldbootfactory.com/pages/locations"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-4 col-sm-6"]')
    for d in div:

        location_type = "".join(d.xpath(".//h3/text()")) or "<MISSING>"
        if location_type == "<MISSING>":
            location_type = "".join(d.xpath(".//preceding-sibling::div[1]//h3/text()"))
        street_address = "".join(d.xpath(".//p/a/text()[1]")) or "<MISSING>"
        if street_address == "<MISSING>":
            continue
        ad = (
            "".join(d.xpath(".//p/a/text()[2]"))
            .replace("Southlake", "Southlake,")
            .strip()
        ) or "<MISSING>"
        if ad == "<MISSING>":
            ad = (
                "".join(d.xpath(".//following-sibling::div[1]//p/a/text()[2]"))
                .replace("\n", "")
                .strip()
            )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()

        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()

        country_code = "US"

        phone = (
            "".join(d.xpath('.//p[contains(text(), "(")]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("Store:") != -1:
            phone = phone.split("Store:")[1].strip()
        location_name = "".join(d.xpath(".//h5/text()"))

        text = "".join(d.xpath(".//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        if city == "Fort Worth":
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            latitude=latitude,
            longitude=longitude,
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
