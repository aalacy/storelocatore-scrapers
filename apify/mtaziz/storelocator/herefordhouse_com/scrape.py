from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgpostal.sgpostal import parse_address_usa
import json
import re
from lxml import html
from sgpostal.sgpostal import parse_address_usa

DOMAIN = "herefordhouse.com"
BASE_URL = "https://www.herefordhouse.com/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_slug(test_dict, location_name):
    url_v = ""
    for k, v in test_dict.items():
        if k.startswith("CustomPage:") and location_name == v["name"]:
            url_v = "https://www.herefordhouse.com" + v["url"]
    return url_v


def get_hoo(sel):
    divs = sel.xpath(
        '//div[contains(@class, "hours")]/div[contains(@class, "hours-entry")]'
    )
    hoo = []
    for div in divs:
        dh = "".join(div.xpath(".//text()"))
        dh = " ".join(dh.split())
        hoo.append(dh)
    hoo = ", ".join(hoo)
    return hoo


def get_rawadd(sel):
    add = sel.xpath('//*[contains(@class, "address-link")]//text()')
    add = [" ".join(i.split()) for i in add]
    add = [i for i in add if i]
    add1 = " ".join(add)
    return add1


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    info = soup.find("script", {"id": "popmenu-apollo-state"})
    info = re.search(r"window\.POPMENU_APOLLO_STATE\s+=\s+(.*);", info.string).group(1)
    info = json.loads(info)
    for key, value in info.items():
        if key.startswith("RestaurantLocation:"):
            with SgRequests() as http:
                location_name = value["name"]
                page_url = get_slug(info, location_name)

                r = http.get(page_url, headers=HEADERS)
                sel = html.fromstring(r.text, "lxml")
                raw_add = get_rawadd(sel)
                hours_of_operation = get_hoo(sel)
                street_address = "".join(
                    sel.xpath('//*[contains(@class, "address-link")]/span/text()')
                )
                street_address = raw_add.split(" ")[-1]

                pai = parse_address_usa(raw_add)
                zip_postal = pai.postcode if pai.postcode is not None else ""
                state = pai.state
                sta = ""
                sta1 = pai.street_address_1
                sta2 = pai.street_address_2
                if sta1 is not None and sta2 is not None:
                    sta = sta1 + ", " + sta2
                elif sta1 is not None and sta2 is None:
                    sta = sta1
                elif sta1 is None and sta2 is not None:
                    sta = sta2
                else:
                    sta = ""
                city = pai.city
                country_code = pai.country
                phone = sel.xpath('//a[contains(@href, "tel:")]/@href')
                phone = "".join(phone).replace("tel:", "")
                store_number = value["id"]
                try:
                    latitude = value["lat"]
                except:
                    latitude = ""
                try:
                    longitude = value["lng"]
                except:
                    longitude = ""

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=sta,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_add,
                )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
