from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jabzboxing.com"
    api_url = "https://www.jabzboxing.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//a[contains(@href, '/locations/')]")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        cms = "".join(d.xpath('.//preceding::h3[text()="COMING SOON"][1]//text()'))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(
                tree.xpath(
                    '//h4[@class="title"]//text() | //h1[@class="f-med large_dark"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()

        street_address = (
            "".join(tree.xpath('//h4[@class="f-30 m-text"]/a/text()[1]')).strip()
            or "<MISSING>"
        )
        ad = "".join(tree.xpath('//h4[@class="f-30 m-text"]/a/text()[2]')).strip()
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"

        state = ad.split(",")[1].split()[0].strip()
        try:
            postal = ad.split(",")[1].split()[1].strip()
        except:
            postal = "<MISSING>"
        country_code = "US"
        city = ad.split(",")[0].strip()
        hours_of_operation = "<MISSING>"
        ll = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "center: new google.maps.LatLng")]/text()'
                )
            )
            or "<MISSING>"
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll != "<MISSING>":
            latitude = ll.split("LatLng(")[1].split(",")[0]
            longitude = ll.split("LatLng(")[1].split(",")[1].split(")")[0]
        if cms == "COMING SOON":
            hours_of_operation = "COMING SOON"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
