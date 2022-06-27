from sgscrape.sgpostal import International_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://hodlservices.ca/atm-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var wf_gmp_maps")]/text()'))
        .split('var wf_gmp_maps = "')[1]
        .split('";')[0]
    )
    jsblock = jsblock.replace("\\", "")
    jsblock = jsblock.split('"pins":')[1].split("}]}]")[0].strip() + "}]"
    js = jsblock.split("},")

    for j in js:

        page_url = "https://hodlservices.ca/atm-locations/"
        icon = j.split('"icon":"')[1].split('"')[0].strip()
        ad = (
            j.split('"address":"')[1]
            .split('"')[0]
            .replace("rn", " ")
            .replace("u00a0", "")
            .strip()
        )

        a = parse_address(International_Parser(), ad)
        location_name = (
            j.split('"tooltip":"')[1].split('"')[0].replace("rn", " ").strip()
        )
        location_type = "<MISSING>"
        if "yellow-dot" in icon:
            location_type = "Sell - Buy location"
        if "green-dot" in icon:
            location_type = "Buy location"
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = ad.split(",")[1].strip()
        if street_address.find("21 Princess St") != -1:
            postal = "L2A 1V7"
        if street_address.find("L8N") != -1:
            street_address = street_address.replace("L8N", "")
            postal = "L8N" + " " + postal
        latitude = j.split('"lat":"')[1].split('"')[0].strip()
        longitude = j.split('"lng":"')[1].split('"')[0].strip()
        phone = j.split("Store:")[1].split("<")[0].strip()
        if phone == "NAtrn" or phone == "NA":
            phone = "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://hodlservices.ca"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
