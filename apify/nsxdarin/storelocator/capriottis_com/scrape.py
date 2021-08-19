from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJRQ2hpc1p1SUExdzk0MVBJTlRKTk1QSXo3bG55RlFWTmNFU2tIRVR0azlieVBEeHowNlNyeVlYZXBDalh0bVZkcmZHdm0zNGUyMG9GM0hYejBVdHBiM0dReWpBeHA1N0NYTVE5WGJoZ09aWmg2djVsQ1hIblE2SkYiLCJqdGkiOiJiMDIyZTA3OWQ4MWFiMGEyNWQ1NTYwYWM4NDFmYTcyNjQ2Y2IzOGY1ZGQxYmE0MWMxODQ4N2ZiNTZhYjY5NjVkMzhkYzlmOWRmNzMwZTYyYiIsImlhdCI6MTYyOTEyNTQyNC44MzE4MTQsIm5iZiI6MTYyOTEyNTQyNC44MzE4MTgsImV4cCI6MTYyOTIxMTgyNC44MDYzNDgsInN1YiI6IiIsInNjb3BlcyI6WyJhbGxlcmdpZXM6aW5kZXgiLCJhbmFseXRpY3NfZXZlbnRzOnNob3dfc2NoZW1hIiwiYmFza2V0X2xveWFsdHk6YXBwbHlfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmRlc3Ryb3lfcmV3YXJkIiwiYmFza2V0X2xveWFsdHk6Z2V0X2FwcGxpZWRfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmdldF9hdmFpbGFibGVfcmV3YXJkcyIsImJhc2tldHM6ZGVzdHJveV9wcm9tb19jb2RlIiwiYmFza2V0czpkZXN0cm95X3dhbnRlZF90aW1lIiwiYmFza2V0czpnZXRfYXZhaWxhYmxlX3dhbnRlZF90aW1lcyIsImJhc2tldHM6bGlzdF9yZXF1aXJlZF92ZXJpZmljYXRpb25zIiwiYmFza2V0czpzZXRfY29udmV5YW5jZSIsImJhc2tldHM6c2hvdyIsImJhc2tldHM6c3RvcmUiLCJiYXNrZXRzOnN0b3JlX2FsbGVyZ2llcyIsImJhc2tldHM6c3RvcmVfcHJvbW9fY29kZSIsImJhc2tldHM6c3RvcmVfd2FudGVkX3RpbWUiLCJiYXNrZXRzOnN1Ym1pdCIsImJhc2tldHM6dmFsaWRhdGVfYmFza2V0IiwiYmFza2V0czp2ZXJpZnlfYmFza2V0IiwiY29uZmlnOnNob3ciLCJncm91cDpvcmRlcmluZ19hcHAiLCJsb2NhdGlvbl9tZW51OnNob3ciLCJsb3lhbHR5OmNoZWNrX3JlZ2lzdHJhdGlvbl9zdGF0dXMiLCJsb3lhbHR5OmNyZWF0ZV9yZWRlbXB0aW9uIiwibG95YWx0eTpmb3Jnb3RfcGFzc3dvcmQiLCJsb3lhbHR5OmluZGV4X3JlZGVlbWFibGVzIiwibG95YWx0eTppbmRleF9yZWRlbXB0aW9ucyIsImxveWFsdHk6cmVnaXN0ZXIiLCJsb3lhbHR5OnJlc2V0X3Bhc3N3b3JkIiwibG95YWx0eTpzaG93X2xveWFsdHlfc3RhdGUiLCJsb3lhbHR5OnNob3dfbWUiLCJsb3lhbHR5OnVwZGF0ZV9tZSIsIm9yZGVyX2xveWFsdHk6Y2xhaW1fcmV3YXJkcyIsIm9yZGVyczpjdXN0b21lcl9hcnJpdmFsIiwib3JkZXJzOmRlc3Ryb3lfZmF2b3JpdGUiLCJvcmRlcnM6ZGlzcGF0Y2hfcmVjZWlwdF9lbWFpbCIsIm9yZGVyczppbmRleF9mYXZvcml0ZXMiLCJvcmRlcnM6aW5kZXhfbXlfb3JkZXJzIiwib3JkZXJzOnN0b3JlX2Zhdm9yaXRlIiwic3RvcmVfbG9jYXRpb25zOmRlc3Ryb3lfZmF2b3JpdGUiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXgiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXhfZmF2b3JpdGVzIiwic3RvcmVfbG9jYXRpb25zOnNob3ciLCJzdG9yZV9sb2NhdGlvbnM6c3RvcmVfZmF2b3JpdGUiLCJ0YWdzOmluZGV4IiwidXBzZWxsczpnZW5lcmF0ZSIsInVzZXJzOmRlc3Ryb3lfc3RvcmVkX2NhcmQiLCJ1c2VyczppbmRleF9zdG9yZWRfY2FyZHMiXX0.guuU74yKC7quND6monnr1_a6ILRVycUq40VHY-ADmGBxiMFF5wk5TgfVoGzxgL_wx_MDXTHl1PPMKvM2g8uok8Mwc7jaWbAHPwmdGCa7nRUoQ8K-cLZTSib0obmu48_Frz0Mh8ZRuVOxsWMSw4OK1y0jHJC5tIjxXPhHqEvr2karyvhYGbbaGMN3YBxS3QdP_l27gpA6DroUYWVmV43_qsLdu7GMSB6Qv6Ezq2yC4zxDJVHm8UKl_6b6W8FJd76hTIULNX44Jtey66TgITMR6I8SWrJAPzNdF52sR4nc9kDFhDgpD4c2Qp3FCGUepgmmUZkMaRwT9wZKzPe-OLTkGIpm1gNRj-iK-KM4gy9b_i9CYMFtqTf6UtOpS1yi5gNyeIJz1G-MYicr1LW8gHxu2jI0S7xze--tipKV_HqXknglfLvOajprPF_UC_lI0avT9OSKMhKmCKMHLdAWekQ8WGeXBai1EQHb9DYLApsbVIrboojqDmfZrI-M6m8n0KSaeQ14_ktMLJI2l1234ugO7Txgd0gsY-YrlASxUe5iZplsEWHI1d0uo7qHMea7JOW9xjxwLWIPNZ2dUIZMVC7gZwW9IAzKeZmIS9O-RxdJLer3q1mh-XSLwKU-NEUcSGqgWM2HzNH4wXn9tUWoiY80Fna1TONAHbD-GRprmrVso9E",
}

logger = SgLogSetup().get_logger("capriottis_com")


def fetch_data():
    for x in range(1, 6):
        url = (
            "https://api.koala.io/v1/ordering/store-locations/?sort[state_id]=asc&sort[label]=asc&include[]=operating_hours&include[]=attributes&include[]=delivery_hours&page="
            + str(x)
            + "&per_page=50"
        )
        r = session.get(url, headers=headers)
        website = "capriottis.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"location_id":"' in line:
                items = line.split('"location_id":"')
                for item in items:
                    if '"latitude":' in item:
                        store = item.split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        name = item.split('"label":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        phone = item.split('"phone_number":"')[1].split('"')[0]
                        add = item.split('"street_address":"')[1].split('"')[0]
                        lurl = (
                            "https://capriottis.olo.com/menu/"
                            + item.split('"slug":"')[1].split('"')[0]
                        )
                        hours = "<INACCESSIBLE>"
                        name = name.replace("\\u2019", "'")
                        yield SgRecord(
                            locator_domain=website,
                            page_url=lurl,
                            location_name=name,
                            street_address=add,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code=country,
                            phone=phone,
                            location_type=typ,
                            store_number=store,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
