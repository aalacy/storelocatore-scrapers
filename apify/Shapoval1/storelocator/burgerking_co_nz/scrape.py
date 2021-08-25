from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.co.nz/"
    page_url = "https://www.burgerking.co.nz/locations?field_geofield_distance[origin][lat]=-36.8484597&field_geofield_distance[origin][lon]=174.76333150000005"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="bk-restaurants"]/ul/li')
    for d in div:
        location_name = "".join(
            d.xpath('.//div[@class="bk-location-title"]/text()')
        ).strip()
        street_address = "".join(d.xpath('.//div[@class="bk-address1"]/text()')).strip()
        state = "".join(d.xpath('.//div[@class="bk-province-name"]/text()'))
        postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
        if postal == "-":
            postal = "<MISSING>"
        country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
        city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
        store_number = "".join(d.xpath('.//div[@class="bk-counter"]/text()'))
        latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
        longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
        phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
        if phone == "0":
            phone = "<MISSING>"
        if phone.find("Restaurant") != -1:
            phone = phone.split("Restaurant: ")[1].split(",")[0].strip()
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday = d.xpath('.//div[contains(@class, "hours")]/text()')
        i = 0
        tmp = []
        for d in days:
            day = d
            times = "".join(weekday[i])
            if times.find("(") != -1:
                times = times.split("(")[0].strip()
            i += 1
            line = f"{day} {times}"
            tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
