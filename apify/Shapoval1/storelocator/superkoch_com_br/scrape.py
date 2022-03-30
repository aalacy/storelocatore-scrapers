from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.superkoch.com.br/"
    page_url = "https://www.superkoch.com.br/nossas-lojas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p/span/strong[contains(text(), "Telefone")]]')
    for d in div:

        location_name = "".join(d.xpath("./p[1]//text()")).strip()
        ad = "".join(d.xpath("./p[2]//text()")).strip()
        if location_name == "Tijucas / Hiper":
            ad = "".join(d.xpath("./p[2]/text()[1]")).replace("\n", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "BR"
        city = a.city or "<MISSING>"
        city = str(city).replace("/", "").strip()
        text = "".join(d.xpath(".//following-sibling::div[1]//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "-27.1274565" and street_address.find("3855 Meia Praia") == -1:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(d.xpath("./p[4]//text()")).replace("Telefone:", "").strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(d.xpath("./p[5]//text()")).replace("Telefone:", "").strip()
                or "<MISSING>"
            )
        hours_of_operation = "".join(d.xpath("./p[3]//text()")).strip()
        if location_name == "Tijucas / Hiper":
            hours_of_operation = (
                "".join(d.xpath("./p[2]/text()[2]")).replace("\n", "").strip()
            )
            phone = (
                "".join(d.xpath("./p[3]//text()")).replace("Telefone:", "").strip()
                or "<MISSING>"
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
            latitude=latitude,
            longitude=longitude,
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
