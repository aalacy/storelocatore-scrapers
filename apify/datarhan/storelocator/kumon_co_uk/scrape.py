from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    start_url = "https://www.kumon.co.uk/find-a-tutor/"
    domain = "kumon.co.uk"
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}

    formdata = {
        "latlon": "0,0",
        "centre_search": "london",
        "chosen_options[1][days_open_monday]": "0",
        "chosen_options[1][days_open_tuesday]": "0",
        "chosen_options[1][days_open_wednesday]": "0",
        "chosen_options[1][days_open_thursday]": "0",
        "chosen_options[1][days_open_friday]": "0",
        "chosen_options[1][days_open_saturday]": "0",
        "chosen_options[1][days_open_sunday]": "0",
        "chosen_options[2][1]": "0",
        "chosen_options[2][2]": "0",
        "chosen_options[3][104]": "0",
        "chosen_options[3][136]": "0",
        "chosen_options[3][138]": "0",
        "widget_search_centres": "",
    }

    response = session.post(start_url, data=formdata, headers=hdr)
    dom = etree.HTML(response.text)

    scraped_urls = []
    all_locations = dom.xpath('//a[contains(@class, "choose-centre-button")]/@href')
    next_page = dom.xpath('//a[small[i[@class="fa fa-chevron-right"]]]/@href')
    while next_page:
        if next_page[0] not in scraped_urls:
            formdata = {
                "centre_search": "london",
                "page": next_page[0].split("=")[-1],
                "chosen_filters": "chosen_options%5B1%5D%5Bdays_open_monday%5D=0&chosen_options%5B1%5D%5Bdays_open_tuesday%5D=0&chosen_options%5B1%5D%5Bdays_open_wednesday%5D=0&chosen_options%5B1%5D%5Bdays_open_thursday%5D=0&chosen_options%5B1%5D%5Bdays_open_friday%5D=0&chosen_options%5B1%5D%5Bdays_open_saturday%5D=0&chosen_options%5B1%5D%5Bdays_open_sunday%5D=0&chosen_options%5B2%5D%5B1%5D=0&chosen_options%5B2%5D%5B2%5D=0&chosen_options%5B3%5D%5B104%5D=0&chosen_options%5B3%5D%5B136%5D=0&chosen_options%5B3%5D%5B138%5D=0",
                "latlon": "0,0",
            }
            response = session.post(start_url, data=formdata, headers=hdr)
            scraped_urls.append(next_page[0])
            dom = etree.HTML(response.text)
            all_locations += dom.xpath(
                '//a[contains(@class, "choose-centre-button")]/@href'
            )
            next_page = dom.xpath('//a[small[i[@class="fa fa-chevron-right"]]]/@href')
            if next_page and next_page[0] in scraped_urls:
                next_page = None

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="text-center"]/text()')[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[0]
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = "UK"
        phone = loc_dom.xpath('//span[@class="number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//table[@class="centre-timings"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
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
