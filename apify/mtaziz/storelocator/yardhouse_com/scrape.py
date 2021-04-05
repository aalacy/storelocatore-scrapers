from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgrequests import SgRequests
from lxml import html
import json


logger = SgLogSetup().get_logger(logger_name="yardhouse_com")
session = SgRequests()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'bm_sz=7DF7AD8819655FF837BC4975BCB8BDDF~YAAQOgrYF6y0+5x4AQAA04XlnQtx98QyzSpjpH6nbdTXRWb1jdHm2z6WtOU02kBiIkXMeJp5cH8ej6CwKXq1EZGFEsWDJefYlMxshbwktCCgsh0CJ9r3bNJgMqen2ftaNPlBogKyfNKqt7cdzMDZNvzWgc15BN1ub64wQlonlyX6ase3QYu0sji981F0a6YIiN0=; at_check=true; AMCVS_13516EE153222FCE0A490D4D%40AdobeOrg=1; _confirmations=[%22group%22]; _abck=28B16E956FEC4A66468F21C254D22060~0~YAAQOgrYF8q0+5x4AQAAaKflnQWWUx0sAPHea63Q8wjlHZpBxQiCLYvG5TsjfYHRpWXoMj95YpUUvWITvhyZhiJVVy6BxTGqR5WrnCK/eFOjX47XlKx6I/I0+w1/nMnaWgz+xxFI9ypCjntcemsN3URPP7cI8wKMJLf72JPXx4nbKWCR0AwKjb2da8KRcCAHcYevoXQ4qO+syPVeFm+weW2/9CPRuqp1ESu5SGN53/skzhYzh86KHlseQhvoWyvNWhy1FLRueeerfWu1ZuzJ8mMAG5llrdIpp34O5KzSxQLhXc+Xw2RKTWFPk/hc23QFMKIjoFU1pkBnXU478mypapTxTJSy6gx424H5TBbdsPajm3vaM4cSJOYeUUhRXgiC0F969vX7o5TMgaWwdZFcVysrGZuuw/TDuKg=~-1~||-1||~-1; emailSignupCounterPerSession=1; DRIREST=4400058@@Glendale - Westgate Entertainment District@@33.53408584*-112.26126437@@9401 West Westgate Blvd@@Glendale@@AZ@@85305@@(623) 872-3900@@Sun-Thu <span class="times">11:00AM-11:30PM</span> <br>Fri-Sat <span class="times">11:00AM-12:30AM</span> <br>@@true@@~@@8315; DRIRESTAURANTID=8315; bm_mi=4AAC737CDAD000D39A4522F97B8191C6~1TclB0KJDnnd/lmNg3sOixu/9rcnYGVcGCv6sYBcBiuU5paVH3zFtY+BmNCZuWhKueWY3oMpRaJaa+58YozphU/mMTaTmt+Ne+Prsxchvw99wb6xkmezVD6AwVo/bdSs2UqY+NqPRVzUuqbNRBxk566XzcggXiJLmr6Voe9JQRgqU1bA4gJumypcurwLkEzkZeDb/T0E3ARjoEAt32fIps8hTF7Ceh27aTG9TFPzXHPkcqqRllLwG7CrHmWRpk+8PObMScUxjkck180TFdL58cGeM7nrsFmhgMj+8y9rr+jxGGHRNoltVDwH4QWytkAE; bm_sv=C11535C794FF9699B0D3FC73AEB24CFE~YWQe5vjn/0I1HP6Rx2/9inmUf106MowMnJYAgziWoqF3HpaFBy1FNjSYFab1kpJqv3/8VY/DGvDadB7LYFTkpVh9JXiFYRcM8RnP5J0awFD64N8mEbMM6W+7eS40uETglqKjwJOumL1Ld6qBt3uDtIfzy3X4j7ZVUsztHLa9JdA=; AKA_A2=A; ak_bmsc=39C3B9873976549ECF1767EE8104F5F517D80A3A770A000021F5696007B43A4E~pliy0fupTPO0/SlfX6mwyusZHAlPzmvyPEKWUHIv0D1o7EvVRV342uf54PbrlriKcr7rJEbrfRu6QN+YD0P8KaR+LJGthOdKuFN9eUX20qcSDTrbHlAvqPeYv5C54V/WDw4n3VkD2niCNY3AKnOFjg7/+A3d+FNhwjniUy9JSyrZK+unrIU6a8Jfhe9lpuMVlBhZyhe58urizH+ku3tnEXoaX39Zyvp3a7bmkj0jVZOncwJjJIwLrEmOakmHRYaVUo4y79IYXzyiyTxRERldRS1OeUA1W7Mpt93qYnSrDjxPikJVgp5jXqf8HxXlsfhUFbnz4Pi9o1nvE/doM2NwvsiocDSuOCF2xomWoX/4AY8DU=; AMCV_13516EE153222FCE0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C18722%7CMCMID%7C39660848108342057661004397067835423471%7CMCOPTOUT-1617568037s%7CNONE%7CvVersion%7C5.2.0; JSESSIONID=F2-eI57gGHGAQ5RleUGVGaHLA-iDmu_S0NFbjqQZFaTRTOCaUGUs!371600789; mbox=PC#331b0d3e8a09488c8aa46af0a1a74078.35_0#1680805639|session#e873857ec89d402ab210afa62aecbbcb#1617561746',
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

locator_domain = "https://www.yardhouse.com"


def fetch_data():

    locs = []
    url = "https://www.yardhouse.com/en-locations-sitemap.xml"
    r = session.get(url, headers=headers)
    logger.info("Pulling Store URLs")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.yardhouse.com/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        r = session.get(loc, headers=headers)
        logger.info(f"Pulling store data from: {loc}")
        data_raw = html.fromstring(r.text, "lxml")
        data_json = data_raw.xpath('//script[@type="application/ld+json"]/text()')[0]
        data_json1 = data_json.replace("\n", "")
        data_json2 = json.loads(data_json1)
        logger.info(f"Pulling the Data from: {loc}")
        if data_json2:
            phone_data = data_json2["telephone"]
            if phone_data == str(0):
                phone_data = "<MISSING>"
            else:
                phone_data = phone_data
            yield SgRecord(
                page_url=loc,
                location_name=data_json2["name"],
                street_address=data_json2["address"]["streetAddress"],
                city=data_json2["address"]["addressLocality"],
                state=data_json2["address"]["addressRegion"],
                zip_postal=data_json2["address"]["postalCode"],
                store_number=data_json2["branchCode"],
                location_type=data_json2["@type"],
                country_code=data_json2["address"]["addressCountry"],
                latitude=data_json2["geo"]["latitude"],
                longitude=data_json2["geo"]["longitude"],
                phone=phone_data,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(data_json2["openingHours"]),
            )
        else:
            continue

    logger.info("Scraping Finished")


if __name__ == "__main__":
    with SgWriter() as writer:
        logger.info("Scraping Started!")
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
