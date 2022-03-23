from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "centurytheatres"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.cinemark.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    r = session.get("https://cinemark.com/full-theatre-list", headers=headers)

    stores_sel = lxml.html.fromstring(r.text)
    links = stores_sel.xpath('//div[@class="columnList wide"]//a/@href')
    for link in links:
        page_url = "https://cinemark.com" + link
        log.info(page_url)
        r1 = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(r1.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')

        try:
            for curr_json in json_list:
                info = "".join(curr_json).strip()
                if info[0] == "{":
                    data = json.loads(info)
                    for address in data["address"]:
                        street_address = address["streetAddress"]
                        city = address["addressLocality"]
                        state = address["addressRegion"]
                        zipp = address["postalCode"]
                        country_code = address["addressCountry"]
                    phone = data["telephone"]
                    location_name = data["name"]
                    log.info(location_name)
                    if "NOW CLOSED".lower() in location_name.lower():
                        continue
                    location_type = data["@type"]
                    try:
                        latitude = (
                            "".join(
                                store_sel.xpath(
                                    '//div[@class="theatreMap"]/a/img/@data-src'
                                )
                            )
                            .split("pp=")[1]
                            .split(",")[0]
                        )
                    except:
                        latitude = "<MISSING>"

                    try:
                        longitude = (
                            "".join(
                                store_sel.xpath(
                                    '//div[@class="theatreMap"]/a/img/@data-src'
                                )
                            )
                            .split("pp=")[1]
                            .split(",")[1]
                            .split("&")[0]
                        )
                    except:
                        longitude = "<MISSING>"

                    yield SgRecord(
                        locator_domain=website,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code=country_code,
                        store_number="<MISSING>",
                        phone=phone if phone else "<MISSING>",
                        location_type=location_type,
                        latitude=latitude if latitude else "<MISSING>",
                        longitude=longitude if longitude else "<MISSING>",
                        hours_of_operation="<MISSING>",
                    )
                    break

        except:
            raise


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
