import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.theroomplace.com/api/commerce/storefront/locationUsageTypes/SP/locations/?pageSize=100&includeAttributeDefinition=true"

    headers = {
        "authority": "www.theroomplace.com",
        "method": "GET",
        "path": "/api/commerce/storefront/locationUsageTypes/SP/locations/?pageSize=100&includeAttributeDefinition=true",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": '_mzvr=oJFFjDZ07UybHrbDHNG_Xw; sb-sf-at-prod=pt=&at=WMsRJ1o3uHPIzPM+RH7rziO4uj2XnkH8CAcUrR5pK9G7b0A3Gzk+30YvBqEacAPwN+0ipvimfft41OF1i8OLt/eeNVZ0hH3LqertBP25JUd/feKU30THq5mB/Vd2t+QWqVEMFq0ObstLGeOjQejruIGPD/TfCZ2lVU6+veNhhHVgLE+t5SBxJy7lUR9Oo8UUBsRyth7IFhbBFPfoQob87d+O3v8iw+gYWqPw5DLgFfzMbqggFnK5mFwErpWD9LvWkiNIsvzIqmk55MpA5K6DojKJ1ctFHNSM6XSMgB+s3aaBelSGkTtIFS/iTppbKzwjmTmuNisJzS5ZLAkQT+wjFA==; _gcl_au=1.1.121714397.1619468651; __attentive_id=7de53867b69047feb668248126b06255; _fbp=fb.1.1619468653875.868466156; __attentive_cco=1619468654553; scarab.visitor=%2259527B39C9A1569%22; t_trp=t_plc=; _mzvs=nn; _mzvt=_mPsWpTjEkK2DK3lmiLgPQ; AKA_A2=A; _gid=GA1.2.1516990442.1621151177; mozucart=%7B%22itemCount%22%3A0%2C%22totalQuantity%22%3A0%2C%22total%22%3A0%2C%22isExpired%22%3Afalse%2C%22hasActiveCart%22%3Atrue%7D; __attentive_ss_referrer="ORGANIC"; __attentive_dv=1; fcaid=66ea49df11f6430c0c87f72ed2c285dd2eeaf62f4fd8c83ffcaa2e4941ed7d99; _mzPc=eyJjb3JyZWxhdGlvbklkIjoiMDE1YjE0OTc5NDNhNGY0ZmJlY2Q1ZmNhOGU4OTA0MjUiLCJpcEFkZHJlc3MiOiIyMTIuMTAyLjYxLjIwOSIsImlzRGVidWdNb2RlIjpmYWxzZSwiaXNDcmF3bGVyIjpmYWxzZSwiaXNNb2JpbGUiOmZhbHNlLCJpc1RhYmxldCI6ZmFsc2UsImlzRGVza3RvcCI6dHJ1ZSwidmlzaXQiOnsidmlzaXRJZCI6Il9tUHNXcFRqRWtLMkRLM2xtaUxnUFEiLCJ2aXNpdG9ySWQiOiJvSkZGakRaMDdVeWJIcmJESE5HX1h3IiwiaXNUcmFja2VkIjpmYWxzZSwiaXNVc2VyVHJhY2tlZCI6ZmFsc2V9LCJ1c2VyIjp7ImlzQXV0aGVudGljYXRlZCI6ZmFsc2UsInVzZXJJZCI6ImEwYzZhOTRjZGI1NTQyNWI5MTBhMDE0ZDBmM2QxMjUyIiwiZmlyc3ROYW1lIjoiIiwibGFzdE5hbWUiOiIiLCJlbWFpbCI6IiIsImlzQW5vbnltb3VzIjp0cnVlLCJiZWhhdmlvcnMiOlsxMDE0LDIyMl19LCJ1c2VyUHJvZmlsZSI6eyJ1c2VySWQiOiJhMGM2YTk0Y2RiNTU0MjViOTEwYTAxNGQwZjNkMTI1MiIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWxBZGRyZXNzIjoiIiwidXNlck5hbWUiOiIifSwiaXNFZGl0TW9kZSI6ZmFsc2UsImlzQWRtaW5Nb2RlIjpmYWxzZSwibm93IjoiMjAyMS0wNS0xNlQwNzo0OTowNi4xNzcxOTUyWiIsImNyYXdsZXJJbmZvIjp7ImlzQ3Jhd2xlciI6ZmFsc2UsImNhbm9uaWNhbFVybCI6Ii9zdG9yZS1sb2NhdG9yIn0sImN1cnJlbmN5UmF0ZUluZm8iOnt9fQ%3d%3d; RT="z=1&dm=theroomplace.com&si=g397rmmi05e&ss=knz1tjxl&sl=0&tt=0"; _ga_KKFKMN1XHG=GS1.1.1621151176.6.1.1621151347.0; _ga=GA1.2.624386355.1619468652; _uetsid=cc690290b61a11eba29d8511b22e8e41; _uetvid=5d7aa3c0a6cd11eb841089f293ec1cd8; __attentive_pv=5',
        "if-none-match": "0754cf336540426885a4859fc18e890b",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["items"]

    data = []

    locator_domain = "theroomplace.com"

    for store in stores:
        location_name = store["name"]
        link = "https://www.theroomplace.com/location/" + location_name.lower().replace(
            " ", "-"
        )
        street_address = store["address"]["address1"].replace("(Route 30)", "").strip()
        if "Main Showroom" in street_address:
            street_address = store["address"]["address3"]
        city = store["address"]["cityOrTown"]
        state = store["address"]["stateOrProvince"]
        zip_code = store["address"]["postalOrZipCode"]
        country_code = store["address"]["countryCode"]
        store_number = store["code"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["geo"]["lat"]
        longitude = store["geo"]["lng"]
        hours_of_operation = ""
        days = store["regularHours"]
        for key, value in days.items():
            value = str(value)
            value = value.split("{'label': '")
            if len(value) == 2:
                value = value[1].split("'")[0]
            hours_of_operation = hours_of_operation + " " + key + " " + str(value)
        if "tuesday  wednesday  thursday  friday  saturday" in hours_of_operation:
            hours_of_operation = (
                hours_of_operation.replace("monday", "monday - saturday")
                .replace("~", "-")
                .split("tuesday")[0]
                .replace("  ", " ")
                .strip()
            )
        hours_of_operation = hours_of_operation.replace(
            "timeZone ['Central Standard Time']", ""
        )
        hours_of_operation = hours_of_operation.replace("AM-", " am -")
        hours_of_operation = hours_of_operation.replace("PM", " pm").strip()

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
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


scrape()
