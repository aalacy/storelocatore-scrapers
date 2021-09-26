from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.hu/"
    page_url = "https://burgerking.hu/locations?field_geofield_distance[origin][lat]=47.502934&field_geofield_distance[origin][lon]=19.034851&locationSearch="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="bk-restaurants"]/ul/li')
    for d in div:

        location_name = "".join(d.xpath('.//div[@class="bk-title"]/text()'))
        street_address = (
            "".join(d.xpath('.//div[@class="bk-address1"]/text()'))
            .replace(", TEGUCIGALPA", "")
            .strip()
        )
        state = "".join(d.xpath('.//div[@class="bk-province-name"]/text()'))
        postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
        country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
        city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
        store_number = "".join(d.xpath('.//div[@class="bk-counter"]/text()'))
        latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
        longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
        phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
        if phone == "0":
            phone = "<MISSING>"
        sundayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_sun_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        sundayClose = (
            "".join(d.xpath('.//div[@class="bk-location_sun_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        mondayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_mon_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        mondayClose = (
            "".join(d.xpath('.//div[@class="bk-location_mon_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        tuesdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_tue_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        tuesdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_tue_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        wednesdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_wed_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        wednesdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_wed_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        thursdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_thu_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        thursdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_thu_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        fridayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_fri_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        fridayClose = (
            "".join(d.xpath('.//div[@class="bk-location_fri_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        saturdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_sat_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        saturdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_sat_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        hours_of_operation = f"Sunday {sundayOpen} - {sundayClose} Monday {mondayOpen} - {mondayClose} Tuesday {tuesdayOpen} - {tuesdayClose} Wednesday {wednesdayOpen} - {wednesdayClose} Thursday {thursdayOpen} - {thursdayClose} Friday {fridayOpen} - {fridayClose} Saturday {saturdayOpen} - {saturdayClose}"

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
