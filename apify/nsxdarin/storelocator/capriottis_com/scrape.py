import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJRQ2hpc1p1SUExdzk0MVBJTlRKTk1QSXo3bG55RlFWTmNFU2tIRVR0azlieVBEeHowNlNyeVlYZXBDalh0bVZkcmZHdm0zNGUyMG9GM0hYejBVdHBiM0dReWpBeHA1N0NYTVE5WGJoZ09aWmg2djVsQ1hIblE2SkYiLCJqdGkiOiJlNWQ2YWEzM2VlNDRjOWM1NzczMzlmMzA3YWE5ZTA3NDkxZTZjYjg4NDZiMzBhYzI5M2NhNDlhMDc2YWYwYjRmMmM3YWExMWE1NjI4YTYwMSIsImlhdCI6MTYyNjcyMzczNCwibmJmIjoxNjI2NzIzNzM0LCJleHAiOjE2MjY4MTAxMzQsInN1YiI6IiIsInNjb3BlcyI6WyJhbGxlcmdpZXM6aW5kZXgiLCJhbmFseXRpY3NfZXZlbnRzOnNob3dfc2NoZW1hIiwiYmFza2V0X2xveWFsdHk6YXBwbHlfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmRlc3Ryb3lfcmV3YXJkIiwiYmFza2V0X2xveWFsdHk6Z2V0X2FwcGxpZWRfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmdldF9hdmFpbGFibGVfcmV3YXJkcyIsImJhc2tldHM6ZGVzdHJveV9wcm9tb19jb2RlIiwiYmFza2V0czpkZXN0cm95X3dhbnRlZF90aW1lIiwiYmFza2V0czpnZXRfYXZhaWxhYmxlX3dhbnRlZF90aW1lcyIsImJhc2tldHM6bGlzdF9yZXF1aXJlZF92ZXJpZmljYXRpb25zIiwiYmFza2V0czpzZXRfY29udmV5YW5jZSIsImJhc2tldHM6c2hvdyIsImJhc2tldHM6c3RvcmUiLCJiYXNrZXRzOnN0b3JlX2FsbGVyZ2llcyIsImJhc2tldHM6c3RvcmVfcHJvbW9fY29kZSIsImJhc2tldHM6c3RvcmVfd2FudGVkX3RpbWUiLCJiYXNrZXRzOnN1Ym1pdCIsImJhc2tldHM6dmFsaWRhdGVfYmFza2V0IiwiYmFza2V0czp2ZXJpZnlfYmFza2V0IiwiY29uZmlnOnNob3ciLCJncm91cDpvcmRlcmluZ19hcHAiLCJsb2NhdGlvbl9tZW51OnNob3ciLCJsb3lhbHR5OmNoZWNrX3JlZ2lzdHJhdGlvbl9zdGF0dXMiLCJsb3lhbHR5OmNyZWF0ZV9yZWRlbXB0aW9uIiwibG95YWx0eTpmb3Jnb3RfcGFzc3dvcmQiLCJsb3lhbHR5OmluZGV4X3JlZGVlbWFibGVzIiwibG95YWx0eTppbmRleF9yZWRlbXB0aW9ucyIsImxveWFsdHk6cmVnaXN0ZXIiLCJsb3lhbHR5OnJlc2V0X3Bhc3N3b3JkIiwibG95YWx0eTpzaG93X2xveWFsdHlfc3RhdGUiLCJsb3lhbHR5OnNob3dfbWUiLCJsb3lhbHR5OnVwZGF0ZV9tZSIsIm9yZGVyX2xveWFsdHk6Y2xhaW1fcmV3YXJkcyIsIm9yZGVyczpjdXN0b21lcl9hcnJpdmFsIiwib3JkZXJzOmRlc3Ryb3lfZmF2b3JpdGUiLCJvcmRlcnM6ZGlzcGF0Y2hfcmVjZWlwdF9lbWFpbCIsIm9yZGVyczppbmRleF9mYXZvcml0ZXMiLCJvcmRlcnM6aW5kZXhfbXlfb3JkZXJzIiwib3JkZXJzOnN0b3JlX2Zhdm9yaXRlIiwic3RvcmVfbG9jYXRpb25zOmRlc3Ryb3lfZmF2b3JpdGUiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXgiLCJzdG9yZV9sb2NhdGlvbnM6aW5kZXhfZmF2b3JpdGVzIiwic3RvcmVfbG9jYXRpb25zOnNob3ciLCJzdG9yZV9sb2NhdGlvbnM6c3RvcmVfZmF2b3JpdGUiLCJ0YWdzOmluZGV4IiwidXBzZWxsczpnZW5lcmF0ZSIsInVzZXJzOmRlc3Ryb3lfc3RvcmVkX2NhcmQiLCJ1c2VyczppbmRleF9zdG9yZWRfY2FyZHMiXX0.OizHuAbKeogDBQ4n13l7cJQAbSKKJ8gGDj615Dy0tHKQJWwInhDhPcTekhDdcSzkwB4Z10Pu2GyZ-prQ1EJkOL4u-Uyf3aRrwqBQqasvMNRNKPmBmtZaEglrIDPsLO8TZYh6jek-XabbMPoPVHJ_hbLcseAOD6xNbudZbsNujpHLrk8UiQOst-EGa9BaGOYCCyTkHokIMhVwK15OdULQ5J9HU-SwVQTwPJKryi4QUYzV-wOZc46iEitUTgpO2JC9xxsYNtPNV2F2oNB67mO5RU8MGRgLgUmZw9V56mi7ZepGRs8igYmPvuoDetwyTtMAxM0n4t1jPq4NEg4D_aGYCrYstaozv-HC2DN1vAyiw4G3TkmYvLN8mOF3699V3_6TQ2AEVB-mOCx4gz_pX2SqJ4tHDlspShB2CPo3nNVk5O5zPr2vVUx7r4lvaUlAlRCGveM4h2rhcJICWZ-KVQRutXGlDjETa30wkDh4GEmbzUQgrVTmzIZPrT-2eQFl9mm22jKIzyuBA_JS6QrFWqnTW-n0pduA3-77a7KNZ8QUeUsnlsv4qUg4HEjBKnR0IdU7omPuLCinuBK0pV-gFU34o1lJsWzsEE1yRh0c-7jOt0LaRJd3f-A-TzoQYxoi_4kE54raJyLRUlTekVhf9xPjVTLLBrXAzJL4EIbfmVdVHuo",
}

logger = SgLogSetup().get_logger("capriottis_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


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
                        yield [
                            website,
                            lurl,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
