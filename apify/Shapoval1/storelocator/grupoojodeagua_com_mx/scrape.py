from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://grupoojodeagua.com.mx/"
    page_url = "https://grupoojodeagua.com.mx/sucursales/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="vc_tta-panel-body"]')
    for d in div:
        info = d.xpath(".//*//text()")
        info = list(filter(None, [a.strip() for a in info]))
        ad = " ".join(info).split("DIRECCIÓN")[1].strip()
        if ad.find("Tel") != -1:
            ad = ad.split("Tel")[0].strip()
        if ad.find("TEL") != -1:
            ad = ad.split("TEL")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        postal = str(postal).replace(".", "").replace("C", "").replace("P", "").strip()
        country_code = "MX"
        if state == "FL":
            country_code = "US"
        city = a.city or "<MISSING>"
        if city == "<MISSING>" and ad.find("Estado de México") != -1:
            city = "Estado de México"
        if city == "<MISSING>" and ad.find("Quintana Roo") != -1:
            city = "Quintana Roo"
        text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone_lst = d.xpath(
            './/*[contains(text(), "Tel")]//text() | .//*[contains(text(), "TEL")]//text()'
        )
        phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
        phone = (
            "".join(phone_lst[0]).replace("TEL.", "").replace("Tel.", "").strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(phone_lst[1]).replace("TEL.", "").replace("Tel.", "").strip()
                or "<MISSING>"
            )
        if phone.find(" ") != -1:
            phone = phone.split(" ")[0].strip()
        hours_of_operation = " ".join(info).split("HORARIO")[1].strip()
        if hours_of_operation.find("Facturación") != -1:
            hours_of_operation = hours_of_operation.split("Facturación")[0].strip()
        if hours_of_operation.find("DIRECCIÓN") != -1:
            hours_of_operation = hours_of_operation.split("DIRECCIÓN")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
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
