from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJRQ2hpc1p1SUExdzk0MVBJTlRKTk1QSXo3bG55RlFWTmNFU2tIRVR0azlieVBEeHowNlNyeVlYZXBDalh0bVZkcmZHdm0zNGUyMG9GM0hYejBVdHBiM0dReWpBeHA1N0NYTVE5WGJoZ09aWmg2djVsQ1hIblE2SkYiLCJqdGkiOiIxZWUzZDM5ZWM5MDQ1OWMzZDIzMDJkZDM1NTI2ZjBhYmUyNjA2NTcyYjgzMDY5ZjIxNDRjODY2ZDQ1NTk0NTNhMzE3YTIwMmJkMjYwMjg1YiIsImlhdCI6MTYzMDQyNDQzNi42MDk0ODksIm5iZiI6MTYzMDQyNDQzNi42MDk0OTQsImV4cCI6MTYzMDUxMDgzNi41OTI1NjQsInN1YiI6IiIsInNjb3BlcyI6WyJhbGxlcmdpZXM6aW5kZXgiLCJhbmFseXRpY3NfZXZlbnRzOnNob3dfc2NoZW1hIiwiYmFza2V0X2xveWFsdHk6YXBwbHlfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmRlc3Ryb3lfcmV3YXJkIiwiYmFza2V0X2xveWFsdHk6Z2V0X2FwcGxpZWRfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmdldF9hdmFpbGFibGVfcmV3YXJkcyIsImJhc2tldHM6ZGVzdHJveV9wcm9tb19jb2RlIiwiYmFza2V0czpkZXN0cm95X3dhbnRlZF90aW1lIiwiYmFza2V0czpnZXRfYXZhaWxhYmxlX3dhbnRlZF90aW1lcyIsImJhc2tldHM6bGlzdF9yZXF1aXJlZF92ZXJpZmljYXRpb25zIiwiYmFza2V0czpzZXRfY29udmV5YW5jZSIsImJhc2tldHM6c2hvdyIsImJhc2tldHM6c3RvcmUiLCJiYXNrZXRzOnN0b3JlX2FsbGVyZ2llcyIsImJhc2tldHM6c3RvcmVfcHJvbW9fY29kZSIsImJhc2tldHM6c3RvcmVfd2FudGVkX3RpbWUiLCJiYXNrZXRzOnN1Ym1pdCIsImJhc2tldHM6dmFsaWRhdGVfYmFza2V0IiwiYmFza2V0czp2ZXJpZnlfYmFza2V0IiwiY29uZmlnOnNob3ciLCJncm91cDpvcmRlcmluZ19hcHAiLCJsb2NhdGlvbl9tZW51OnNob3ciLCJsb3lhbHR5OmNoZWNrX3JlZ2lzdHJhdGlvbl9zdGF0dXMiLCJsb3lhbHR5OmNyZWF0ZV9yZWRlbXB0aW9uIiwibG95YWx0eTpmb3Jnb3RfcGFzc3dvcmQiLCJsb3lhbHR5OmluZGV4X3JlZGVlbWFibGVzIiwibG95YWx0eTppbmRleF9yZWRlbXB0aW9ucyIsImxveWFsdHk6cmVnaXN0ZXIiLCJsb3lhbHR5OnJlc2V0X3Bhc3N3b3JkIiwibG95YWx0eTpzaG93X2xveWFsdHlfc3RhdGUiLCJsb3lhbHR5OnNob3dfbWUiLCJsb3lhbHR5OnVwZGF0ZV9tZSIsIm9yZGVyX2xveWFsdHk6Y2xhaW1fcmV3YXJkcyIsIm9yZGVyczpjdXN0b21lcl9hcnJpdmFsIiwib3JkZXJzOmRlc3Ryb3lfZmF2b3JpdGUiLCJvcmRlcnM6ZGlzcGF0Y2hfcmVjZWlwdF9lbWFpbCIsIm9yZGVyczppbmRleF9mYXZvcml0ZXMiLCJvcmRlcnM6aW5kZXhfbXlfb3JkZXJzIiwib3JkZXJzOnN0b3JlX2Zhdm9yaXRlIiwic3RvcmVfbG9jYXRpb25zOmRlc3Ryb3lfZmF2b3JpdGUiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXgiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXhfZmF2b3JpdGVzIiwic3RvcmVfbG9jYXRpb25zOnNob3ciLCJzdG9yZV9sb2NhdGlvbnM6c3RvcmVfZmF2b3JpdGUiLCJ0YWdzOmluZGV4IiwidXBzZWxsczpnZW5lcmF0ZSIsInVzZXJzOmRlc3Ryb3lfc3RvcmVkX2NhcmQiLCJ1c2VyczppbmRleF9zdG9yZWRfY2FyZHMiXX0.JUiCD2Ey2ugolHBlpMyBcgoOeUhTtVgf7WOBLI87aUJUpi6p9rANAyUsAeAKDXsU4saf055nhik3Zr6M42StqG3Aku441G0En_Hl-cSezK8JByZWG2YsrCUA3j1iO1VDzlUUkRDnehYi6GKB9xVdogBBX2tgYey-7SpO1NMMR4U3nXWsDq5eKhBqQW84_wwg6iVBzWv-Dw7JOyrkdRnqUwU6p9SDFG54Iac0eCBw4AfuU1CozBuL0EYFIdXa45XUImf0POU7aLrxkoETWogzJPatitr3het5jBsRck3YYUZDcADnu3dp8HzwpA-2Xfur_AcYsDan3giJXEPqlxq3JeIEmdoPd7-IuTXVqz-uUJ1yTi3Rih6DlF9rtzlMjDTt5l5c3pXs7uOs9pTpcCM1AsqBbhTT5ov1shWNu_jSbpffnEhxQZNjDVO49B8IWM3hqD9Zg04vpqstMBDro7fP9purqehqtgzXxqp2kDSpWovsVPwzsL5cce88SS3r5iz7UN_NU1HcThrSdxpnDLAEsoRCQ1Jm9EJHvUDU-W9eYoYFNTJhkNCBUuOkehmJwIs_Gs91VqWnsjT3SLiG8NcxPCH-xuSdGOMeCuRUw62ExUDarnlFOkP002-GhlbpILmlFR0wc25m_80iL_RQIkWi-Gq6KgyBV9aXZTr_BRh3kDY",
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
