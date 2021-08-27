from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobell.co.in/"
    api_url = "https://www.tacobell.co.in/find-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="find-Us-Branches"]')
    i = 0
    for d in div:

        page_url = "https://www.tacobell.co.in/find-us"
        location_name = "".join(d.xpath(".//h5/text()"))
        ad = (
            " ".join(d.xpath('.//p[@class="findus_addr"]/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "India"
        city = a.city or "<MISSING>"
        ll = eval(
            "".join(tree.xpath('//script[contains(text(), "var markers")]/text()'))
            .split("JSON.parse('")[1]
            .split("');")[0]
            .strip()
        )
        latitude = "".join(ll[i]).split(",")[0].strip()
        longitude = "".join(ll[i]).split(",")[1].strip()
        i += 1
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        if phone == "NA":
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//a[@class="btn-ordernow"]/preceding::p[1]//text()'))
            .replace("\n", "")
            .replace("Opening hours ·", "")
            .replace("OPEN:", "")
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad.replace("Address:", "").strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
