# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as BS

website = "ovcb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Referer": "https://www.ovcb.com/branches_ovcb_modesto_mchenry.html",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.ovcb.com/branches.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sections = stores_sel.xpath('//div[contains(@id,"subPages")]')
    for sec in sections:
        titles = sec.xpath('span[@class="contentTitle"]/text()')
        urls_section = sec.xpath("ul")
        for index in range(0, len(titles)):
            if "ATM Only Locations" == titles[index]:
                continue

            stores = urls_section[index].xpath("li/a/@href")
            for store_url in stores:
                page_url = "https://www.ovcb.com/" + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                soup = BS(store_req.text, "lxml")
                raw_info = list(
                    soup.find_all("p", {"id": "pBranchInfo"})[0].stripped_strings
                )
                location_name = "".join(
                    store_sel.xpath("//h1[@class='columnTitle']/text()")
                ).strip()
                location_type = "<MISSING>"
                locator_domain = website
                phone = ""
                street_address = raw_info[0].strip()
                city = raw_info[1].strip().split(",")[0].strip()
                state = raw_info[1].strip().split(",")[1].strip().split(" ")[0].strip()
                zipp = raw_info[1].strip().split(",")[1].strip().split(" ")[-1].strip()
                hours_of_operation = ""
                for info_index in range(0, len(raw_info)):
                    if "Phone:" in raw_info[info_index].strip():
                        phone = (
                            raw_info[info_index + 1]
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "")
                            .strip()
                        )
                    if "Fax:" in raw_info[info_index].strip():
                        try:
                            hours_of_operation = (
                                " ".join(raw_info[info_index + 1 :])
                                .strip()
                                .replace("Lobby ", "")
                                .replace("Lobby:", "")
                                .strip()
                                .encode("ascii", "replace")
                                .decode("utf-8")
                                .replace("?", "")
                                .strip()
                            )
                            if "Drive-Up" in hours_of_operation:
                                hours_of_operation = hours_of_operation.split(
                                    "Drive-Up"
                                )[0].strip()
                        except:
                            pass
                        break

                country_code = "US"
                store_number = "<MISSING>"

                latitude = ""
                longitude = ""
                map_link = "".join(
                    store_sel.xpath('//a[contains(text(),"Map This Location")]/@href')
                ).strip()
                if "sll=" in map_link:
                    latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                    longitude = (
                        map_link.split("sll=")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split("&")[0]
                        .strip()
                    )
                    if "maps.google." in longitude:
                        latitude = (
                            map_link.split("sll=")[-1].strip().split(",")[0].strip()
                        )
                        longitude = (
                            map_link.split("sll=")[-1]
                            .strip()
                            .split(",")[1]
                            .strip()
                            .split("&")[0]
                            .strip()
                        )

                elif "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
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
