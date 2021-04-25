# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "usbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://locations.usbank.com/index.html"
    base_url = "https://locations.usbank.com"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//li/a[@class="stateListItemLink"]/@href')
    url_list = []
    for state_url in states:
        cities_req = session.get(base_url + state_url, headers=headers)
        cities_sel = lxml.html.fromstring(cities_req.text)
        cities = cities_sel.xpath('//li/a[@class="cityListItemLink"]/@href')
        for city_url in cities:
            stores_req = session.get(base_url + city_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//div[@class="locationsList"]/ul/li')

            for store in stores:
                title = "".join(
                    store.xpath('.//div[@class="locDetails"]//h2//text()')
                ).strip()
                if "and" in title:
                    title = (
                        "".join(title.split("and")[0]).strip()
                        + " and "
                        + "".join(title.split("and")[1]).strip()
                    )
                if "Branch and ATM" in title:
                    page_url = (
                        base_url
                        + "".join(
                            store.xpath(
                                './/a[contains(text(),"See branch details")]/@href'
                            )
                        ).strip()
                    )
                    if page_url in url_list:
                        continue

                    url_list.append(page_url)

                    log.info(page_url)
                    store_req = session.get(page_url)
                    store_sel = lxml.html.fromstring(store_req.text)

                    locator_domain = website

                    location_name = title
                    street_address = "".join(
                        store_sel.xpath(
                            '//div[@class="branchAddress"]/div[@class="h5heading branchStr"]/text()'
                        )
                    ).strip()
                    city_state_zip = (
                        "".join(
                            store_sel.xpath(
                                '//div[@class="branchAddress"]/div[@class="h5heading branchLoc"]/text()'
                            )
                        )
                        .strip()
                        .replace("\n", "")
                        .strip()
                    )

                    city = city_state_zip.strip().split(",")[0].strip()
                    state = (
                        city_state_zip.strip()
                        .split(",")[-1]
                        .strip()
                        .split(" ")[0]
                        .strip()
                    )
                    zip = (
                        city_state_zip.strip()
                        .split(",")[-1]
                        .strip()
                        .split(" ")[-1]
                        .strip()
                    )
                    country_code = "US"

                    phone = "".join(
                        store_sel.xpath('//div[@class="branchAddress"]//a//text()')
                    ).strip()

                    store_number = "<MISSING>"
                    location_type = "Branch and ATM"

                    hours = store_sel.xpath(
                        '//table[@class="lobbyTimes"]//tr[position()>1]'
                    )
                    hours_list = []
                    for hour in hours:
                        day = "".join(hour.xpath("th//text()")).strip()
                        time = "".join(hour.xpath("td//text()")).strip()
                        hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude = ""
                    try:
                        latitude = (
                            store_req.text.split("var locationLatitude = ")[1]
                            .strip()
                            .split(";")[0]
                            .strip()
                        )
                    except:
                        pass

                    longitude = ""
                    try:
                        longitude = (
                            store_req.text.split("var locationLongitude = ")[1]
                            .strip()
                            .split(";")[0]
                            .strip()
                        )
                    except:
                        pass

                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )

                else:
                    if "ATM" in title:
                        page_url = base_url + city_url
                        location_name = title
                        address = store.xpath('.//div[@class="locDetails"]/p/text()')
                        street_address = address[0].strip()
                        city = address[-1].strip().split(",")[0].strip()
                        state = (
                            address[-1]
                            .strip()
                            .split(",")[-1]
                            .strip()
                            .split(" ")[0]
                            .strip()
                        )
                        zip = (
                            address[-1]
                            .strip()
                            .split(",")[-1]
                            .strip()
                            .split(" ")[-1]
                            .strip()
                        )
                        country_code = "US"
                        location_type = "ATM"
                        store_number = "<MISSING>"
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        yield SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
