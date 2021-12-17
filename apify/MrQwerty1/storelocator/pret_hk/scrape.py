import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_phone(text):
    return text.replace("Tel", "").replace(":", "").replace(".", "").strip()


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pret.hk/en-HK/find-a-pret"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'entries')]/text()"))
    text = text.split('"entries":')[1].split("}}]}}],")[0] + "}}]}}]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("title")
        raw_address = j["body"]["content"][0]["content"][0]["value"]
        try:
            phone = get_phone(j["body"]["content"][1]["content"][0]["value"])
        except:
            phone = SgRecord.MISSING
        if "Tel" in raw_address and phone == SgRecord.MISSING:
            phone = get_phone(raw_address.split("Tel")[-1])
            raw_address = raw_address.split("\n")[0].strip()
        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="HK",
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pret.hk/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
