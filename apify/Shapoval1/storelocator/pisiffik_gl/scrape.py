from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pisiffik.gl"
    api_url = "https://www.pisiffik.gl/gl/content/44-pisiniarfik-ilinnut-qaninneq"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./strong[contains(text(), "Åbningstider:")]]')
    for d in div:
        types = "".join(d.xpath(".//preceding::img[1]/@src"))
        location_type = "<MISSING>"
        if "pisiffik.png" in types or "Pisiffik_logo" in types:
            location_type = "Pisiffik"
        info = d.xpath(".//preceding::p[1]//text()")
        info = list(filter(None, [a.strip() for a in info]))
        tmp_ad = []
        page_url = "https://www.pisiffik.gl/gl/content/44-pisiniarfik-ilinnut-qaninneq"
        location_name = str(info[0])
        for b in info:
            if "@" not in b and "+" not in b:
                tmp_ad.append(b)
        ad = " ".join(tmp_ad).replace(f"{location_name}", "").strip() or "<MISSING>"
        if location_name.find("Box 61, 3900 Nuuk") != -1:
            ad = " ".join(location_name.split(",")[1:])
            location_name = location_name.split(",")[0].strip()
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "")
            .strip()
            .replace("<Missing>", "<MISSING>")
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        street_address = street_address or ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "GL"
        city = a.city or "<MISSING>"
        table_id = "".join(
            d.xpath(
                ".//preceding::div[@class='wpb_tab ui-tabs-panel wpb_ui-tabs-hide vc_clearfix'][1]/@id"
            )
        )
        if city == "<MISSING>":
            city = "".join(d.xpath(f'.//preceding::a[@href="#{table_id}"]/text()'))
        if "Ilulissat" in ad:
            city = "Ilulissat"
        if "Aasiaat" in ad:
            city = "Aasiaat"
        if "Sisimiut" in ad:
            city = "Sisimiut"
        if "Maniitsoq" in ad:
            city = "Maniitsoq"
        if "Nuuk" in ad or "Nuussuaq" in ad:
            city = "Nuuk"
        if "Qaqortoq" in ad or "Sanatorievej" in ad:
            city = "Qaqortoq"
        tmp_phone = []
        for i in info:
            if "+" in i:
                tmp_phone.append(i)

        phone = "".join(tmp_phone).replace("Tlf :", "") or "<MISSING>"
        if phone == "+299":
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//following::table[1]//tr/td//text()"))
            .replace("\n", "")
            .strip()
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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
