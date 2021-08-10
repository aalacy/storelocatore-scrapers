from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJRQ2hpc1p1SUExdzk0MVBJTlRKTk1QSXo3bG55RlFWTmNFU2tIRVR0azlieVBEeHowNlNyeVlYZXBDalh0bVZkcmZHdm0zNGUyMG9GM0hYejBVdHBiM0dReWpBeHA1N0NYTVE5WGJoZ09aWmg2djVsQ1hIblE2SkYiLCJqdGkiOiIyNjNmYjllZWVlYjFkZGQ1ODNmMTc1NjBiNjE5OTU5ZGU0N2EzMTRmNmFiNTdlY2FmMDk1YzdlYzFmYWMxYjNlMmYyZGYyYjZlNDJjYTU1NSIsImlhdCI6MTYyNzkyNjg2NS4zNDI1OSwibmJmIjoxNjI3OTI2ODY1LjM0MjU5NiwiZXhwIjoxNjI4MDEzMjY1LjMyMTA3OSwic3ViIjoiIiwic2NvcGVzIjpbImFsbGVyZ2llczppbmRleCIsImFuYWx5dGljc19ldmVudHM6c2hvd19zY2hlbWEiLCJiYXNrZXRfbG95YWx0eTphcHBseV9yZXdhcmRzIiwiYmFza2V0X2xveWFsdHk6ZGVzdHJveV9yZXdhcmQiLCJiYXNrZXRfbG95YWx0eTpnZXRfYXBwbGllZF9yZXdhcmRzIiwiYmFza2V0X2xveWFsdHk6Z2V0X2F2YWlsYWJsZV9yZXdhcmRzIiwiYmFza2V0czpkZXN0cm95X3Byb21vX2NvZGUiLCJiYXNrZXRzOmRlc3Ryb3lfd2FudGVkX3RpbWUiLCJiYXNrZXRzOmdldF9hdmFpbGFibGVfd2FudGVkX3RpbWVzIiwiYmFza2V0czpsaXN0X3JlcXVpcmVkX3ZlcmlmaWNhdGlvbnMiLCJiYXNrZXRzOnNldF9jb252ZXlhbmNlIiwiYmFza2V0czpzaG93IiwiYmFza2V0czpzdG9yZSIsImJhc2tldHM6c3RvcmVfYWxsZXJnaWVzIiwiYmFza2V0czpzdG9yZV9wcm9tb19jb2RlIiwiYmFza2V0czpzdG9yZV93YW50ZWRfdGltZSIsImJhc2tldHM6c3VibWl0IiwiYmFza2V0czp2YWxpZGF0ZV9iYXNrZXQiLCJiYXNrZXRzOnZlcmlmeV9iYXNrZXQiLCJjb25maWc6c2hvdyIsImdyb3VwOm9yZGVyaW5nX2FwcCIsImxvY2F0aW9uX21lbnU6c2hvdyIsImxveWFsdHk6Y2hlY2tfcmVnaXN0cmF0aW9uX3N0YXR1cyIsImxveWFsdHk6Y3JlYXRlX3JlZGVtcHRpb24iLCJsb3lhbHR5OmZvcmdvdF9wYXNzd29yZCIsImxveWFsdHk6aW5kZXhfcmVkZWVtYWJsZXMiLCJsb3lhbHR5OmluZGV4X3JlZGVtcHRpb25zIiwibG95YWx0eTpyZWdpc3RlciIsImxveWFsdHk6cmVzZXRfcGFzc3dvcmQiLCJsb3lhbHR5OnNob3dfbG95YWx0eV9zdGF0ZSIsImxveWFsdHk6c2hvd19tZSIsImxveWFsdHk6dXBkYXRlX21lIiwib3JkZXJfbG95YWx0eTpjbGFpbV9yZXdhcmRzIiwib3JkZXJzOmN1c3RvbWVyX2Fycml2YWwiLCJvcmRlcnM6ZGVzdHJveV9mYXZvcml0ZSIsIm9yZGVyczpkaXNwYXRjaF9yZWNlaXB0X2VtYWlsIiwib3JkZXJzOmluZGV4X2Zhdm9yaXRlcyIsIm9yZGVyczppbmRleF9teV9vcmRlcnMiLCJvcmRlcnM6c3RvcmVfZmF2b3JpdGUiLCJzdG9yZV9sb2NhdGlvbnM6ZGVzdHJveV9mYXZvcml0ZSIsInN0b3JlX2xvY2F0aW9uczppbmRleCIsInN0b3JlX2xvY2F0aW9uczppbmRleF9mYXZvcml0ZXMiLCJzdG9yZV9sb2NhdGlvbnM6c2hvdyIsInN0b3JlX2xvY2F0aW9uczpzdG9yZV9mYXZvcml0ZSIsInRhZ3M6aW5kZXgiLCJ1cHNlbGxzOmdlbmVyYXRlIiwidXNlcnM6ZGVzdHJveV9zdG9yZWRfY2FyZCIsInVzZXJzOmluZGV4X3N0b3JlZF9jYXJkcyJdfQ.uJa4ll_RxJ0qc-8po9FUMFbocbb5Dr3n4GoUy-HgILE5q3-AE-PMgzJv4Pjpy9VAB96LPbWhO0nQ6w06jOJ8jWxGaT-MsTatghKjZ4f3rZbC9f0qZ8aNtJ_rIGl7QukJmA91L3X1JzgT2QHySIUVMZfMNo7wY9Bj4GyzbVoymq9NzR3JHL3fPk4WqAJUKg5I8PdQU_AbnAMz1dtLS7F5lUWCRG5YQ5WKUxk8cBjA3e3KvZOdoDKs6q0Uq4aj55qpVO_CnU19Tj8XyZOl5NqXc4JK6Jg9kCMA5eLcZqK_96LdhjaFzXqAVHD7tpvc2ZQPHYvi7E0IAoWjRgb-nQEEfwPSEHVJp5z3cxG6RMsWgdm8Gmm9quld7ea8w3nJlZ-NVu97AqOIPLQyVb3L9VH-wMPMicNpc4ugkAucWgBf-4v5InpHx5_urLG_9a5uTYp1egsQKydedMVlGzVvNIfR1rdU-BsAAnZJQlY6UIkJ5SXUgJmlZMtME8oJTuzbSv-UK8d1zr0gROhtdiqBmj-5GiWYA1Ko1CViTY85xNx3EvMuEq9o1fXCTzlq8cAkQAzkaBdSZe18tXHDkFv_RABmrtJWc7Q2ZranoVN4vhSytQK6gN_MnTuyXBL0uIUdOOJRJrPbrXnX4Pnkk9fXdw1fN2OPBalFa-imszCd5XXCTXE",
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
