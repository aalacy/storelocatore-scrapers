from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cinnaboncyprus.com"
    api_url = "https://www.cinnaboncyprus.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h2[@style="font-size: 20px;color: #ffffff;text-align: left;font-family:Arimo;font-weight:700;font-style:normal"]'
    )
    for d in div:

        page_url = "https://www.cinnaboncyprus.com/locations/"
        location_name = "".join(d.xpath(".//text()"))
        ad = (
            " ".join(d.xpath(".//following-sibling::div[1]//p[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        if ad == "Corner Apostolou Pavlou and":
            ad = (
                ad
                + " "
                + " ".join(d.xpath(".//following-sibling::div[1]//p[2]/text()"))
                .replace("\n", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Cyprus"
        city = a.city or "<MISSING>"
        if city.find("Strovolos") != -1:
            city = city.replace("Strovolos", "").strip()
        phone = (
            "".join(d.xpath('.//following::a[contains(@href, "tel")][1]//text()'))
            .replace("Tel:", "")
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
