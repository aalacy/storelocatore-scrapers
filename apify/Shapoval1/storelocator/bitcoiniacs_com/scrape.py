from sgscrape.sgpostal import International_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://bitcoiniacs.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLB3LzU1KL8pR0lIpLEotKlKwMdJRyUvPSSzKUrHQNdZRyEwviM1OA2g2VagE9LBn7"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["data"]:

        page_url = "https://bitcoiniacs.com/find-bitcoin-atm/"
        desc = j.get("description") or "<MISSING>"
        info, hours = "<MISSING>", "<MISSING>"
        if desc != "<MISSING>":
            a = html.fromstring(desc)
            info = " ".join(a.xpath("//p[1]//text()"))
            hours = " ".join(a.xpath("//p[2]//text()"))
        ad = j.get("address")
        a = parse_address(International_Parser(), ad)
        location_name = j.get("title")
        location_type = "<MISSING>"
        if info.find("<MISSING>") == -1:
            location_type = "ATM" + " " + info.split(",")[1].strip()
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        if "".join(location_name).find("Philippines") != -1:
            country_code = "Philippines"
        if city == "<MISSING>":
            city = ad.split(",")[1].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = hours or "<MISSING>"

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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://bitcoiniacs.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
