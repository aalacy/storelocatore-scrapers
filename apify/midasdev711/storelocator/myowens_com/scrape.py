from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.myowens.com/"
    page_url = "https://www.myowens.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//table[@class="locateTable"]')
    for d in div:

        location_name = (
            "".join(d.xpath('.//preceding::div[@class="locateHeader"][1]//text()'))
            + " "
            + "".join(d.xpath('.//preceding::div[@class="locateTitle2"][1]//text()'))
        )
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//a[contains(@href, "maps")]//text()'))
        ad = "".join(
            d.xpath('.//p[./a[contains(@href, "maps")]]/following-sibling::p/text()')
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    './/td[./p/a[contains(@href, "maps")]]/following-sibling::td[1]/p[1]/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    f'.//td[./p[contains(text(), "{phone}")]]/following-sibling::td//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if latitude == "<MISSING>":
            r = session.get(
                "https://www.myowens.com/wp-admin/admin-ajax.php?action=store_search&lat=40.58654&lng=-122.39168&max_results=2500&search_radius=50000&autoload=1",
                headers=headers,
            )
            js = r.json()
            for j in js:
                adr = j.get("address")
                if street_address == adr:
                    latitude = j.get("lat")
                    longitude = j.get("lng")
                if (
                    "Infusion" in j.get("store")
                    and "3860" in adr
                    and "Infusion" in location_name
                    and "3860" in street_address
                ):
                    latitude = j.get("lat")
                    longitude = j.get("lng")
                if (
                    "Equipment" in j.get("store")
                    and "3860" in adr
                    and "Equipment" in location_name
                    and "3860" in street_address
                ):
                    latitude = j.get("lat")
                    longitude = j.get("lng")

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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
