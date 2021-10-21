from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "staffmark.com"
    start_url = "http://staffmark.com/locations/Default.aspx"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
    view_gen = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
    validation = dom.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]

    formdata = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": view_gen,
        "__EVENTVALIDATION": validation,
        "txtCity": "",
        "ddState": "",
        "txtZip": "",
        "ddDist": "100",
        "btnSearchLocations": "Search",
        "as_fid": "",
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.post(start_url, data=formdata, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//table[@width="100%"]/tr')

    for poi_html in list(set(all_locations)):
        check = " ".join(poi_html.xpath(".//text()"))
        if "unhandled exception was generated" in check:
            continue
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//span[@class="textBold18"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath('.//a[contains(@href, "/maps/")]/@href')
        if address_raw:
            address_raw = address_raw[0].split("/")[-1].split("+")
            street_address = address_raw[0]
            city = address_raw[1].replace(",", "")
            state = address_raw[2].replace(",", "")
            zip_code = address_raw[3].replace(",", "")
        else:
            address_raw = poi_html.xpath('.//td[@align="right"]/text()')
            address_raw = [elem.strip() for elem in address_raw if elem.strip()]
            if not address_raw:
                continue
            street_address = address_raw[0]
            city = address_raw[1].split(",")[0]
            state = address_raw[1].split(",")[-1].split()[0]
            zip_code = address_raw[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            './/span[@class="textBold18"]/following-sibling::text()'
        )[0].strip()
        phone = phone.replace(" phone", "") if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
