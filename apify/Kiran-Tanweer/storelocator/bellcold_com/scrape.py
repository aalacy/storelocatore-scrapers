from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bellcold.com"
    api_url = "https://www.bellcold.com/contact/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="et_pb_blurb_container"]')
    for d in div:

        page_url = "https://www.bellcold.com/contact/"
        location_name = "".join(d.xpath(".//h4//text()"))
        ad = (
            " ".join(d.xpath('.//div[@class="et_pb_blurb_description"]/p[1]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        map_link = "".join(d.xpath(".//preceding::iframe[1]/@src"))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "Bellingham Waterfront Warehouse" in location_name:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Tel:")]/a[1]/text()'))
            or "<MISSING>"
        )
        r = session.get("https://www.bellcold.com/locations/", headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            "".join(
                tree.xpath('//strong[contains(text(), "Hours of Operation")]/text()')
            )
            .replace("Hours of Operation", "")
            .strip()
        )
        slug = tree.xpath(
            '//strong[contains(text(), "Hours of Operation")]/following-sibling::text()'
        )
        for s in slug:
            s_slug = str(s).split(":")[0].strip()
            if (
                s_slug.lower() in location_name.lower()
                or s_slug.lower() in street_address.lower()
            ):
                hours_of_operation = (
                    hours_of_operation + " " + str(s).split(":")[1].strip()
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
