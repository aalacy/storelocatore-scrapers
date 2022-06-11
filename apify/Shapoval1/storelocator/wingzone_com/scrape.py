import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wingzone.com"
    page_url = "https://www.wingzone.com/locations"

    r = session.get(page_url)
    tree = html.fromstring(r.content)
    li = tree.xpath('//li[@class="location"]')
    for j in li:
        ad = j.xpath('.//span[@class="address"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))

        street_address = (
            ", ".join(ad[:-1])
            .replace("Reitz Student Union", "")
            .replace("Page Manor Shopping Center", "")
            .replace("Sheppard Mini Mall Food Court", "")
            .replace("Hub Student Center", "")
            .strip()
        )
        line = ad[-1]
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        postal = line.split()[-1]
        state = line.replace(postal, "").replace(".", "").strip()
        country_code = "US"
        store_number = "".join(j.xpath("./@data-loc-id"))
        slug = "".join(j.xpath(".//a[@class='website btn v3 small']/@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(j.xpath('.//div[@class="title"]/h4/text()'))
        phone = "".join(j.xpath('.//a[@class="phone"]/text()'))
        latitude = "".join(j.xpath("./@data-latitude")) or "<MISSING>"
        longitude = "".join(j.xpath("./@data-longitude")) or "<MISSING>"
        text = "".join(tree.xpath(f"//div[@data-loc-id={store_number}]/ul/@data-hours"))
        text = "[" + text.replace("][", "],[").replace("[", "{").replace("]", "}") + "]"
        js = json.loads(text)
        tmp = []
        for s in js:
            day = s.get("Interval")
            start = "".join(s.get("OpenTime"))[:-3]
            close = "".join(s.get("CloseTime"))[:-3]
            if s.get("Closed") == "1":
                line = f"{day} : Closed"
            else:
                line = f"{day} : {start} - {close}"
            tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=" ".join(ad),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
