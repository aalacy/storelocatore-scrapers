# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "berluti.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "store.berluti.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    # Requests sorts cookies= alphabetically
    # 'cookie': 'route=1651229838.497.9567.132960; device_view=full; _gcl_au=1.1.486805058.1651229841; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2022-04-29%2015%3A57%3A20%7C%7C%7Cep%3Dhttps%3A%2F%2Fstore.berluti.com%2F%7C%7C%7Crf%3D%28none%29; sbjs_first_add=fd%3D2022-04-29%2015%3A57%3A20%7C%7C%7Cep%3Dhttps%3A%2F%2Fstore.berluti.com%2F%7C%7C%7Crf%3D%28none%29; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; bridge-vid=34a899f2-e96e-4af6-ab60-c36f52a44dd6; euconsent-v2=CPSXeoAPSXeoAAHABBENCMCgAIAAAAAAAAAAAAAAAAAA.cAAAAAAAAAAA; _ga=GA1.3.130067645.1651229843; dw=1; dw_cookies_accepted=1; PHPSESSID=15c4c5d5db0b056cc051ebc94a2c593c; cookieconsent_status=allow; sbjs_udata=vst%3D2%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F100.0.4896.127%20Safari%2F537.36; sbjs_session=pgs%3D1%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fstore.berluti.com%2F; bridge-sid=41266fb3-d5d2-435c-be90-2926f11cdcaf; _uetsid=83383840cd4211eca54cd7ae10208c2a; _uetvid=649639c06edd11ec82e665c093bad17f; _gid=GA1.3.33413762.1651844610; _gat_bridge=1; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+06+2022+18%3A43%3A30+GMT%2B0500+(Pakistan+Standard+Time)&version=6.16.0&hosts=&consentId=c8195df5-e425-4822-96d5-75b53d71319a&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0005%3A0&AwaitingReconsent=false; _clck=4zbmv0|1|f18|0; _clsk=1b03xdr|1651844611619|1|1|d.clarity.ms/collect; RT="sl=1&ss=1651844605731&tt=5517&obo=0&bcn=%2F%2F684d0d4c.akstat.io%2F&sh=1651844611260%3D1%3A0%3A5517&dm=berluti.com&si=776fbc72-f882-4d28-b193-e08485c94639&ld=1651844611262&nu=&cl=1651844629254&r=https%3A%2F%2Fstore.berluti.com%2F&ul=1651844629267"',
    "referer": "https://store.berluti.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://store.berluti.com/"
    with SgRequests() as session:
        home_req = session.get(search_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)
        countries = home_sel.xpath('//select[@id="country-input"]/option/@value')
        for country in countries:
            params = {
                "countries[]": country,
                "query": "",
                "lat": "",
                "lon": "",
                "geo": "0",
            }

            stores_req = session.get(
                "https://store.berluti.com/search",
                params=params,
                headers=headers,
            )
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = list(
                set(stores_sel.xpath('//a[contains(text(),"Go to store")]/@href'))
            )
            for store_url in stores:
                page_url = "https://store.berluti.com" + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                for js in json_list:
                    if json.loads(js, strict=False)["@type"] == "LocalBusiness":
                        store_json = json.loads(js, strict=False)
                        locator_domain = website

                        store_number = "<MISSING>"

                        location_type = "<MISSING>"
                        location_name = store_json["name"]

                        street_address = store_json["address"]["streetAddress"]
                        city = store_json["address"]["addressLocality"]
                        state = "<MISSING>"
                        zip = store_json["address"]["postalCode"]

                        country_code = store_json["address"]["addressCountry"]

                        phone = store_json["telephone"].replace("+1", "").strip()

                        hours = store_sel.xpath(
                            '//div[@id="lf-parts-opening-hours-content"]/div'
                        )
                        hours_list = []
                        for hour in hours:
                            day = "".join(hour.xpath("span/text()")).strip()
                            raw_time = (
                                "".join(hour.xpath("div//text()"))
                                .strip()
                                .replace("\n", "")
                                .strip()
                            )
                            if "-" in raw_time:
                                time = (
                                    raw_time.split("-")[0].strip()
                                    + "-"
                                    + raw_time.split("-")[1].strip()
                                )
                            else:
                                time = raw_time
                            hours_list.append(day + ":" + time)

                        hours_of_operation = (
                            "; ".join(hours_list)
                            .strip()
                            .replace("\n", "")
                            .strip()
                            .replace("Today opening hours", "")
                            .strip()
                        )

                        latitude, longitude = (
                            store_json["geo"]["latitude"],
                            store_json["geo"]["longitude"],
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
                        break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
