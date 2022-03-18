from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.com.br/"
    api_url = "https://johnsonfitness.com.br/contato-compra-de-produtos"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://johnsonfitness.com.br/contato-compra-de-produtos"
    location_name = (
        "".join(
            tree.xpath(
                '//img[contains(@src, "Johnson-Fitness-Store-São-Paulo-office-and-showroom")]/@src'
            )
        )
        .split("/02/")[1]
        .split(".")[0]
        .replace("-", " ")
        .strip()
    )
    info = tree.xpath(
        '//div[./div/h4[text()="SHOWROOM"]]/following-sibling::div//text()'
    )
    info = list(filter(None, [a.strip() for a in info]))
    ad = " ".join(info[:-1]).strip()
    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    postal = postal.replace("CEP", "").strip()
    country_code = "BR"
    city = a.city or "<MISSING>"
    city = city.replace("/", "").strip()
    phone = "".join(info[-1]).strip()
    hours_of_operation = "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
