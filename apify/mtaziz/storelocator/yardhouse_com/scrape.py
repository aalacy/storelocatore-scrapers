from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from lxml import html
import json
import time

DOMAIN = "yardhouse.com"
logger = SgLogSetup().get_logger(logger_name="yardhouse_com")
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'bm_sz=7DF7AD8819655FF837BC4975BCB8BDDF~YAAQOgrYF6y0+5x4AQAA04XlnQtx98QyzSpjpH6nbdTXRWb1jdHm2z6WtOU02kBiIkXMeJp5cH8ej6CwKXq1EZGFEsWDJefYlMxshbwktCCgsh0CJ9r3bNJgMqen2ftaNPlBogKyfNKqt7cdzMDZNvzWgc15BN1ub64wQlonlyX6ase3QYu0sji981F0a6YIiN0=; at_check=true; AMCVS_13516EE153222FCE0A490D4D%40AdobeOrg=1; _confirmations=[%22group%22]; _abck=28B16E956FEC4A66468F21C254D22060~0~YAAQOgrYF8q0+5x4AQAAaKflnQWWUx0sAPHea63Q8wjlHZpBxQiCLYvG5TsjfYHRpWXoMj95YpUUvWITvhyZhiJVVy6BxTGqR5WrnCK/eFOjX47XlKx6I/I0+w1/nMnaWgz+xxFI9ypCjntcemsN3URPP7cI8wKMJLf72JPXx4nbKWCR0AwKjb2da8KRcCAHcYevoXQ4qO+syPVeFm+weW2/9CPRuqp1ESu5SGN53/skzhYzh86KHlseQhvoWyvNWhy1FLRueeerfWu1ZuzJ8mMAG5llrdIpp34O5KzSxQLhXc+Xw2RKTWFPk/hc23QFMKIjoFU1pkBnXU478mypapTxTJSy6gx424H5TBbdsPajm3vaM4cSJOYeUUhRXgiC0F969vX7o5TMgaWwdZFcVysrGZuuw/TDuKg=~-1~||-1||~-1; emailSignupCounterPerSession=1; DRIREST=4400058@@Glendale - Westgate Entertainment District@@33.53408584*-112.26126437@@9401 West Westgate Blvd@@Glendale@@AZ@@85305@@(623) 872-3900@@Sun-Thu <span class="times">11:00AM-11:30PM</span> <br>Fri-Sat <span class="times">11:00AM-12:30AM</span> <br>@@true@@~@@8315; DRIRESTAURANTID=8315; bm_mi=4AAC737CDAD000D39A4522F97B8191C6~1TclB0KJDnnd/lmNg3sOixu/9rcnYGVcGCv6sYBcBiuU5paVH3zFtY+BmNCZuWhKueWY3oMpRaJaa+58YozphU/mMTaTmt+Ne+Prsxchvw99wb6xkmezVD6AwVo/bdSs2UqY+NqPRVzUuqbNRBxk566XzcggXiJLmr6Voe9JQRgqU1bA4gJumypcurwLkEzkZeDb/T0E3ARjoEAt32fIps8hTF7Ceh27aTG9TFPzXHPkcqqRllLwG7CrHmWRpk+8PObMScUxjkck180TFdL58cGeM7nrsFmhgMj+8y9rr+jxGGHRNoltVDwH4QWytkAE; bm_sv=C11535C794FF9699B0D3FC73AEB24CFE~YWQe5vjn/0I1HP6Rx2/9inmUf106MowMnJYAgziWoqF3HpaFBy1FNjSYFab1kpJqv3/8VY/DGvDadB7LYFTkpVh9JXiFYRcM8RnP5J0awFD64N8mEbMM6W+7eS40uETglqKjwJOumL1Ld6qBt3uDtIfzy3X4j7ZVUsztHLa9JdA=; AKA_A2=A; ak_bmsc=39C3B9873976549ECF1767EE8104F5F517D80A3A770A000021F5696007B43A4E~pliy0fupTPO0/SlfX6mwyusZHAlPzmvyPEKWUHIv0D1o7EvVRV342uf54PbrlriKcr7rJEbrfRu6QN+YD0P8KaR+LJGthOdKuFN9eUX20qcSDTrbHlAvqPeYv5C54V/WDw4n3VkD2niCNY3AKnOFjg7/+A3d+FNhwjniUy9JSyrZK+unrIU6a8Jfhe9lpuMVlBhZyhe58urizH+ku3tnEXoaX39Zyvp3a7bmkj0jVZOncwJjJIwLrEmOakmHRYaVUo4y79IYXzyiyTxRERldRS1OeUA1W7Mpt93qYnSrDjxPikJVgp5jXqf8HxXlsfhUFbnz4Pi9o1nvE/doM2NwvsiocDSuOCF2xomWoX/4AY8DU=; AMCV_13516EE153222FCE0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C18722%7CMCMID%7C39660848108342057661004397067835423471%7CMCOPTOUT-1617568037s%7CNONE%7CvVersion%7C5.2.0; JSESSIONID=F2-eI57gGHGAQ5RleUGVGaHLA-iDmu_S0NFbjqQZFaTRTOCaUGUs!371600789; mbox=PC#331b0d3e8a09488c8aa46af0a1a74078.35_0#1680805639|session#e873857ec89d402ab210afa62aecbbcb#1617561746',
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://www.yardhouse.com/en-locations-sitemap.xml"
    r = http.get(url, headers=headers)
    logger.info("Pulling Store URLs")
    for line in r.iter_lines():
        line = str(line)
        if "<loc>https://www.yardhouse.com/locations/" in line:
            loc = line.split("<loc>")[1].split("<")[0]
            logger.info(loc)
            state.push_request(SerializableRequest(url=loc))
    return True


def get_hoo(url_store, http):
    r_hoo = http.get(url_store, headers=headers)
    data_raw = html.fromstring(r_hoo.text, "lxml")
    xpath_hoo = '//div[h2[contains(text(), "HOURS")]]/div/ul/li//text()'
    hoo_raw = data_raw.xpath(xpath_hoo)
    hoo_raw = "".join(hoo_raw).split()
    hoo_raw = "; ".join(hoo_raw)
    hoo_raw = hoo_raw.split("None")
    hoo_raw = [
        i.replace(";", "")
        .replace(")", "")
        .replace("(", "")
        .replace("Today", "")
        .strip()
        for i in hoo_raw
        if i
    ]
    hoo_clean = "; ".join(hoo_raw)
    if hoo_clean:
        return hoo_clean
    else:
        return MISSING


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    idx = 0
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        logger.info(f"Pulling the Data from: {idx} <<:>> {next_r.url}")
        time.sleep(3)
        data_raw = html.fromstring(r.text, "lxml")
        data_json = data_raw.xpath('//script[@type="application/ld+json"]/text()')[0]
        data_json1 = data_json.replace("\n", "")
        data = json.loads(data_json1)
        got_data = False
        for i in range(5):
            if not got_data:
                try:
                    location_name = data["name"]
                    if location_name:
                        got_data = True
                except:
                    pass
                if not got_data:
                    logger.info("Retrying data pull ..")
                    r = http.get(next_r.url, headers=headers)
                    time.sleep(10)
                    data_raw = html.fromstring(r.text, "lxml")
                    data_json = data_raw.xpath(
                        '//script[@type="application/ld+json"]/text()'
                    )[0]
                    data_json1 = data_json.replace("\n", "")
                    data = json.loads(data_json1)
            else:
                break

        if got_data:

            page_url = next_r.url if next_r.url else MISSING

            sa = data["address"]["streetAddress"]
            street_address = sa if sa else MISSING

            city = data["address"]["addressLocality"]
            city = city if city else MISSING

            state = data["address"]["addressRegion"]
            state = state if state else MISSING

            zipcode = data["address"]["postalCode"]
            zip_postal = zipcode if zipcode else MISSING

            store_number = data["branchCode"] if data["branchCode"] else MISSING

            location_type = data["@type"] if data["@type"] else MISSING

            cc = data["address"]["addressCountry"]
            country_code = cc if cc else MISSING

            lat = data["geo"]["latitude"]
            latitude = lat if lat else MISSING

            lng = data["geo"]["longitude"]
            longitude = lng if lng else MISSING

            try:
                phone = data["telephone"]
            except KeyError:
                phone = MISSING

            if MISSING not in phone and phone == str(0):
                phone = MISSING

            if data["openingHours"]:
                hours_of_operation = "; ".join(data["openingHours"])
            else:
                hours_of_operation = get_hoo(next_r.url, http)

            raw_address = MISSING
            idx += 1
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        else:
            continue


def scrape():
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
