from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url1 = "https://www.ditkasrestaurants.com/"
    session1 = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session1.get(api_url1, headers=headers)
    tree = html.fromstring(r.text)
    jsblock1 = (
        "".join(tree.xpath('//script[contains(text(), "subOrganization")]/text()'))
        .split('"subOrganization": [')[1]
        .split("],")[0]
    )

    api_url2 = "https://www.grill89.com/"
    session2 = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session2.get(api_url2, headers=headers)
    tree = html.fromstring(r.text)
    jsblock2 = (
        "".join(tree.xpath('//script[contains(text(), "subOrganization")]/text()'))
        .split('"subOrganization":')[1]
        .split(', "sameAs":')[0]
    )
    jsblock = jsblock1 + "," + jsblock2
    js = eval(jsblock)
    for j in js:
        a = j.get("address")
        page_url = j.get("url")
        location_name = j.get("name")
        location_type = j.get("@type")
        street_address = a.get("streetAddress")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = "USA"
        city = a.get("addressLocality")
        phone = j.get("telephone")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        latitude = "".join(tree.xpath("//div/@data-gmaps-lat"))
        longitude = "".join(tree.xpath("//div/@data-gmaps-lng"))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[text()="Hours:"]]/following-sibling::p[contains(text(), "am")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./a[contains(@href, "tel")]]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.ditkasrestaurants.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
