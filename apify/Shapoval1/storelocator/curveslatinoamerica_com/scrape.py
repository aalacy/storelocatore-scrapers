from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curveslatinoamerica.com/"
    api_url = "https://curveslatinoamerica.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="dropdown-item font-weight-lighter text-white"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://curveslatinoamerica.com/{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="card"]')
        for d in div:

            location_name = (
                "".join(d.xpath('.//p[@class="lead"]//text()')) or "<MISSING>"
            )
            ad = "".join(d.xpath('.//small[@class="text-muted"]/text()[1]'))
            info = d.xpath('.//small[@class="text-muted"]/text()')
            info = list(filter(None, [a.strip() for a in info]))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            postal = postal.replace(".", "").replace("CP", "").strip()
            country_code = slug.split(".")[0].capitalize().strip()
            city = location_name
            phone = (
                "".join(d.xpath('.//small[@class="text-muted"]/text()[2]'))
                .replace("\n", "")
                .replace("Teléfonos:", "")
                .replace("Teléfono:", "")
                .replace("Teléfono;", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find("|") != -1:
                phone = phone.split("|")[0].strip()
            hours_of_operation = (
                " ".join(info).split("Horario:")[1].strip() or "<MISSING>"
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
