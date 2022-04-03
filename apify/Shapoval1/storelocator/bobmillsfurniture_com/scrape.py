from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bobmillsfurniture.com/"
    api_url = "https://www.bobmillsfurniture.com/contacts"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3")

    for d in div:

        page_url = (
            "".join(d.xpath(".//following::*[@data-href][5]/@data-href"))
            .replace("#virtual-tour", "")
            .strip()
        )
        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        street_address = (
            "".join(d.xpath("./following::span[1]/span[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath("./following::span[1]/span[2]/text()"))
            .replace("\n", "")
            .strip()
        )

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        text = "".join(d.xpath(".//following::*[@data-href][4]/@data-href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath(".//following::*[@data-href][1]/text()"))
        hours_of_operation = (
            "".join(d.xpath(".//following::*[10]//text()"))
            .replace("Get Directions", "")
            .replace("Store Hours", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
