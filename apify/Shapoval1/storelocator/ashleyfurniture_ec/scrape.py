from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://ashleyfurniture.ec/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//map/area")
    for d in div:
        locator_domain = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}location.html"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="StoreAddress"]')
        for d in div:
            location_name = "".join(d.xpath("./a[1]/strong/text()"))
            info = d.xpath(".//text()")
            info = list(filter(None, [a.strip() for a in info]))
            street_address = (
                "".join(d.xpath("./a[1]/text()[1]")).replace("\n", "").strip()
            )
            ad = "".join(d.xpath("./a[1]/text()[3]")).replace("\n", "").strip()
            country_code = "Ecuador"
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            try:
                postal = ad.split(",")[1].split()[1].strip()
            except:
                postal = "<MISSING>"
            latitude = (
                "".join(
                    d.xpath(
                        './/preceding::script[contains(text(), "addMarker")]/text()'
                    )
                )
                .split("addMarker('")[1]
                .split("'")[0]
                .strip()
            )
            longitude = (
                "".join(
                    d.xpath(
                        './/preceding::script[contains(text(), "addMarker")]/text()'
                    )
                )
                .split("addMarker('")[1]
                .split(",")[1]
                .replace("'", "")
                .strip()
            )
            phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            tmp = []
            for i in info:
                if ":" in i and "-" in i:
                    tmp.append(i)
            hours_of_operation = ", ".join(tmp)

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
