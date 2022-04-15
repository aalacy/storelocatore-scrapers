from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pitapit.ie/"
    api_url = "https://pitapit.ie/find-a-location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="View in Google Maps"]')
    for d in div:

        page_url = "https://pitapit.ie/find-a-location/"
        location_name = (
            "".join(d.xpath(".//preceding::h2[1]//text()")).replace("\n", "").strip()
        )
        ad = " ".join(d.xpath(".//preceding::p[4]//text()")).replace("\n", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        city = a.city or "<MISSING>"
        if street_address.find("Dublin 1") != -1:
            street_address = street_address.replace("Dublin 1", "").strip()
            city = "Dublin"
        postal = (
            " ".join(d.xpath(".//preceding::p[3]//text()")).replace("\n", "").strip()
        )
        country_code = "IE"
        text = "".join(d.xpath(".//@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//preceding::p[1]//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if hours_of_operation.find(" Opening") != -1:
            hours_of_operation = "Coming Soon"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
