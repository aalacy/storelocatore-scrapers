from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harveynorman.ie/"
    api_url = "https://hnie-assets.s3-eu-west-1.amazonaws.com/Javascript/store-finder-hours.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    div = r.text.split("},")[:-1]
    for d in div:

        ad = d.split('"storeAddress": "')[1].split('",')[0].strip()
        a = html.fromstring(ad)
        info_add = a.xpath("//*//text()")
        info_add = list(filter(None, [b.strip() for b in info_add]))
        page_url = "https://www.harveynorman.ie/store-finder.html"
        location_name = (
            d.split('"storeName": "')[1]
            .split('",')[0]
            .replace("&#40;", "(")
            .replace("&#41;", ")")
            .replace("\\", "")
            .replace("<small>", "")
            .replace("</small>", "")
            .replace("&amp;", "&")
            .strip()
        )
        street_address = " ".join(info_add[:-2]).strip()
        postal = "".join(a.xpath("//text()[last()]"))
        country_code = "IE"
        city = (
            "".join(a.xpath("//text()[last() - 1]"))
            .replace("14", "")
            .replace("24", "")
            .replace("15", "")
            .replace("18", "")
            .strip()
        )
        map_link = d.split('"storeMap": "')[1].split('",')[0]
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            d.split('"storePhone": "')[1]
            .split('",')[0]
            .replace("&#40;", "(")
            .replace("&#41;", ")")
            .strip()
        )
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for c in days:
            day = c
            times = d.split(f'"{c}StoreHours": "')[1].split('",')[0].strip()
            line = f"{day} {times}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=" ".join(info_add),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
