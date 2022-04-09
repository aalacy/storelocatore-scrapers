from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://smallcakescupcakery.com/"
    api_url = "https://smallcakescupcakery.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location py-3"]')
    for d in div:

        page_url = (
            "".join(d.xpath('.//a[./span[text()="Visit Website"]]/@href')) or api_url
        )
        location_name = "".join(d.xpath(".//h3//text()")).replace("\n", "").strip()
        if (
            location_name.find("Coming Soon") != -1
            or location_name.find("coming soon") != -1
        ):
            continue
        ad = (
            " ".join(d.xpath("./span[position() < 3]/text()")).replace("\n", "").strip()
        )

        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        if "Dubai" in ad:
            country_code = "Dubai"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath(".//span[last()]//text()"))
            .replace("Visit Website", "")
            .strip()
        )
        if (
            not phone.replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .isdigit()
        ):
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
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
