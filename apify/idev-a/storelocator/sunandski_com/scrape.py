import csv
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.sunandski.com"
    headers = {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "Content-type": "application/json",
        "Cookie": "SSSC=775.G6920904069410341529.1|58529.2105822:59550.2130380; sb-sf-at-prod=pt=&at=T9cKOqLkilGWdTIlqz+IKPQDNYYs4c1IXNW+QLF0sihnVDeqmYumuxPSWSs7leknUsE0/0T8Kyo2/yAxIdaIZGwnOwu6N3wtrq8zOP85ERkWbwi7iUMot325Grm8XOgjmTSrANKWfNtTDqzpyaSbeatVeRhJEHN+nGEsfSgiDEJKlsW70LWtNlZreQ1iioivEBtHpKLM5kfqtm4CWdp0WlWXUgzUEC68YVkppdOTwPB+xeS7Em6ZrzJkBwptmSTIIkjm1pgG6RfoJ0EXcvR/o75WXAaXKcvLCJLGb+Dx0R9bR0TI005VlfHFMWaFc9cf; sb-sf-at-prod-s=pt=&at=T9cKOqLkilGWdTIlqz+IKPQDNYYs4c1IXNW+QLF0sihnVDeqmYumuxPSWSs7leknUsE0/0T8Kyo2/yAxIdaIZGwnOwu6N3wtrq8zOP85ERkWbwi7iUMot325Grm8XOgjmTSrANKWfNtTDqzpyaSbeatVeRhJEHN+nGEsfSgiDEJKlsW70LWtNlZreQ1iioivEBtHpKLM5kfqtm4CWdp0WlWXUgzUEC68YVkppdOTwPB+xeS7Em6ZrzJkBwptmSTIIkjm1pgG6RfoJ0EXcvR/o75WXAaXKcvLCJLGb+Dx0R9bR0TI005VlfHFMWaFc9cf&dt=2021-01-23T10:42:31.4337571Z; SSID=CACyih0cAAAAAACV_QtgmULCJZX9C2ABAAAAAAAAAAAAlf0LYAC7bJ7oAAHMgSAAlf0LYAEAoeQAA94hIACV_QtgAQA; _mzvt=N1PslzwGZES_qBahpHRTmQ; _mzvs=nn; _mzvr=50-0iZ_jckSWuqI_zSCVyA; mt.v=2.1441278668.1611398556569; _gcl_au=1.1.2021847244.1611398563; _ga=GA1.2.1956764696.1611398564; _gid=GA1.2.613881265.1611398564; __asc=aa8848911772ed6d586e5722f99; __auc=aa8848911772ed6d586e5722f99; __ctmid=600bfda70003d18a630086fc; __ctmid=600bfda70003d18a630086fc; _fbp=fb.1.1611398570075.660636652; _pin_unauth=dWlkPVpXTTFPR0prWWpBdFptWTBaQzAwT0RZNExUZ3paR0l0TkRZME9EazNPR0ZrTXpjNA; bn_u=6928681074245904318; mozucartcount=%7B%223dce41b3fb9e4cd7aca562f886f14fbe%22%3A0%7D; addshoppers.com=2%7C1%3A0%7C10%3A1611398576%7C15%3Aaddshoppers.com%7C44%3ANzRkMmMzYTQ0YWZhNDBiMGI4ZjIzNzQ4Y2QwYmIyODQ%3D%7C1c2d91bb5beecdf41106c0d520d1e3ee3e1289a875b0b2f3389497af1404cb84; asScore=0; asGeoStateCheck=TX; asGeoCheck=Plano; addshop-pillMessage-viewed=1; addshop-pillMessage-viewed=1; addshopPeekShown=1; bn_ec=%7B%22a%22%3A%22c%22%2C%22c%22%3A%22d%26g%26s%22%2C%22d%22%3A%22https%3A%2F%2Fwww.sunandski.com%2F%3FBNConditionCode%3Dd%26g%26s%22%2C%22r%22%3A%22%22%2C%22t%22%3A1611398619413%2C%22u%22%3A%226928681074245904318%22%2C%22trackingData%22%3Anull%2C%22dd%22%3A%22https%3A%2F%2Fwww.sunandski.com%2Flocations%22%2C%22l%22%3A%22%20Stores%22%2C%22de%22%3A%7B%22ti%22%3A%22Ski%20%26%20Snowboard%2C%20Bikes%2C%20Clothing%20%26%20Footwear%20-%20Sun%20%26%20Ski%20Sports%22%2C%22nw%22%3A287%2C%22nl%22%3A802%7D%7D; asPageViews=2; addshopQuizAbandon=1; SSRT=vv4LYAADAA; _dc_gtm_UA-396722-7=1; _uetsid=bb6f2ab05d6711ebadbe919b96b10bc1; _uetvid=bb6f5a405d6711ebb6ceeb93132a9a6f; _mzPc=eyJjb3JyZWxhdGlvbklkIjoiZmJhMTRmZGVlMDUyNDYwMzg5ZGJmYjQwYjM2MDRkNjgiLCJpcEFkZHJlc3MiOiIxMDQuMjAwLjE0Mi4yMzgiLCJpc0RlYnVnTW9kZSI6ZmFsc2UsImlzQ3Jhd2xlciI6ZmFsc2UsImlzTW9iaWxlIjpmYWxzZSwiaXNUYWJsZXQiOmZhbHNlLCJpc0Rlc2t0b3AiOnRydWUsInZpc2l0Ijp7InZpc2l0SWQiOiJOMVBzbHp3R1pFU19xQmFocEhSVG1RIiwidmlzaXRvcklkIjoiNTAtMGlaX2pja1NXdXFJX3pTQ1Z5QSIsImlzVHJhY2tlZCI6ZmFsc2UsImlzVXNlclRyYWNrZWQiOmZhbHNlfSwidXNlciI6eyJpc0F1dGhlbnRpY2F0ZWQiOmZhbHNlLCJ1c2VySWQiOiIzZGNlNDFiM2ZiOWU0Y2Q3YWNhNTYyZjg4NmYxNGZiZSIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWwiOiIiLCJpc0Fub255bW91cyI6dHJ1ZSwiYmVoYXZpb3JzIjpbMTAxNF19LCJ1c2VyUHJvZmlsZSI6eyJ1c2VySWQiOiIzZGNlNDFiM2ZiOWU0Y2Q3YWNhNTYyZjg4NmYxNGZiZSIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWxBZGRyZXNzIjoiIiwidXNlck5hbWUiOiIifSwiaXNFZGl0TW9kZSI6ZmFsc2UsImlzQWRtaW5Nb2RlIjpmYWxzZSwibm93IjoiMjAyMS0wMS0yM1QxMDo0NzoyNy42OTI5MDk5WiIsImNyYXdsZXJJbmZvIjp7ImlzQ3Jhd2xlciI6ZmFsc2V9LCJjdXJyZW5jeVJhdGVJbmZvIjp7fX0%3d; __kla_id=eyIkcmVmZXJyZXIiOnsidHMiOjE2MTEzOTg1NzMsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd3d3LnN1bmFuZHNraS5jb20vIn0sIiRsYXN0X3JlZmVycmVyIjp7InRzIjoxNjExMzk4ODUxLCJ2YWx1ZSI6IiIsImZpcnN0X3BhZ2UiOiJodHRwczovL3d3dy5zdW5hbmRza2kuY29tLyJ9fQ==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-vol-catalog": "1",
        "x-vol-currency": "USD",
        "x-vol-locale": "en-US",
        "x-vol-master-catalog": "1",
        "x-vol-site": "16493",
        "x-vol-tenant": "11961",
    }
    res = session.get(
        "https://www.sunandski.com/api/commerce/storefront/locationUsageTypes/SP/locations/?sortBy=name%20asc&filter=locationType.Code%20eq%20ST&includeAttributeDefinition=true",
        headers=headers,
    )
    store_list = json.loads(res.text)["items"]
    data = []
    for store in store_list:
        location_name = store["name"].replace("&amp;", "")
        if location_name == "Chantilly":
            continue
        street_address = (
            store["address"]["address1"]
            + " "
            + (
                store["address"]["address2"]
                if "address2" in store["address"].keys()
                else ""
            )
        )
        street_address = street_address.strip()
        city = store["address"]["cityOrTown"]
        state = store["address"]["stateOrProvince"]
        zip = store["address"]["postalOrZipCode"]
        country_code = store["address"]["countryCode"] or "<MISSING>"
        phone = store["phone"] or "<MISSING>"
        location_type = store["locationTypes"][0]["name"]
        store_number = store["code"]
        latitude = store["geo"]["lat"]
        longitude = store["geo"]["lng"]
        hours_of_operation = " "
        for x in store["regularHours"]:
            hours_of_operation += x + ": " + store["regularHours"][x]["label"] + " "
        hours_of_operation = hours_of_operation.strip()
        for x in store["attributes"]:
            if x["fullyQualifiedName"] == "tenant~store-details-url":
                page_url = base_url + x["values"][0]

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
