from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

log = sglog.SgLogSetup().get_logger(logger_name="bigmamaspizza.com")


def fetch_data():
    headers = {
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    with SgRequests(
        proxy_country="us",
        dont_retry_status_codes=([404]),
        verify_ssl=False,
        retries_with_fresh_proxy_ip=20,
    ) as session:
        r = session.get(
            "https://big-mamas-and-papas-pizzeria-locations.brygid.online/zgrid/themes/13278/portal/carryout.jsp",
            headers=headers,
        )
        soup = bs(r.text, "lxml")
        for location in soup.find("ul", {"class": "locations-list"}).find_all(
            "li", {"class": "location"}
        ):
            page_url = location.find("a", text=re.compile("Order Online"))
            hours_of_operation = "<MISSING>"
            if page_url:
                page_url = page_url["href"]
                log.info(page_url)
                store_sel = lxml.html.fromstring(
                    session.get(page_url, headers=headers).text
                )
                try:
                    hours = store_sel.xpath('//div[@id="store-hours"]/table//tr')
                    hours_list = []
                    for hour in hours:
                        day = "".join(hour.xpath("td[1]//text()")).strip()
                        time = "".join(hour.xpath("td[2]//text()")).strip()
                        if len(time) > 0:
                            hours_list.append(day + time)

                    hours_of_operation = "; ".join(hours_list).strip()
                except:
                    hours_of_operation = "<MISSING>"
            else:
                page_url = "<MISSING>"
                try:
                    hours_of_operation = location.find(
                        "a", {"class": "btn store-order"}
                    ).text
                except:
                    pass

            location_details = list(location.stripped_strings)
            locator_domain = "https://bigmamaspizza.com"
            location_name = location_details[0]
            street_address = location_details[1]
            city = location_details[2].split(",")[0]
            state = location_details[2].split(",")[1].split(" ")[-2]
            zip = location_details[2].split(",")[1].split(" ")[-1]
            country_code = "US"
            store_number = "<MISSING>"
            phone = location_details[3]
            location_type = "big mama's paap's pizzaria"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = (
                hours_of_operation.replace(
                    "WE ARE CLOSED EARLY AND CANNOT PROCESS YOUR ORDERS FOR TODAY. PLEASE FEEL FREE TO SUBMIT AN ONLINE ORDER NOW FOR A FUTURE DATE.",
                    "",
                )
                .strip()
                .replace(
                    "WE ARE CLOSED AND CANNOT PROCESS YOUR ORDERS FOR TODAY. PLEASE FEEL FREE TO SUBMIT AN ONLINE ORDER NOW FOR A FUTURE DATE.",
                    "",
                )
                .strip()
            )
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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
