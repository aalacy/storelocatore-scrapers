import re
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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.peaveymart.com/api/commerce/storefront/locationUsageTypes/SP/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "referer": "https://www.peaveymart.com/store-locator",
        "cookie": "sb-sf-at-prod-s=at=LUUXx5Ca0tujZAMzXEBq6oO4yGqj2%2BoI4Ue7hEsqBsDrt5Yf1ktYF6luqtKFkGInVj05Cm%2FcRQNGZgEH50CY7FnGvEa%2F4mjOPcMNuf1uDsO4yZbiwXaI17GbzE0SJDkF2GF7JyirAeu5FjWXe0bDcPEL5q7iTgJ8rPwYWrRyCaZr%2BXkN90HbkCVdF0mR77fzmbcPqeLlFuSC1o4AlvZFDVhyMxGF2Xu7YOuJk%2F1e6%2BosWSIdMPl8nlPR9m7xNwD7aDu1AAOVgVwkAF63b0iXOUiGb2cFd2sgw5BAHtAJARsX8JHQhO%2FmfZIEAJ6uGw8ZrR4suxqPCBccteAgTvHp%2Fg%3D%3D&dt=2021-06-10T10%3A38%3A56.9768742Z; sb-sf-at-prod=at=LUUXx5Ca0tujZAMzXEBq6oO4yGqj2%2BoI4Ue7hEsqBsDrt5Yf1ktYF6luqtKFkGInVj05Cm%2FcRQNGZgEH50CY7FnGvEa%2F4mjOPcMNuf1uDsO4yZbiwXaI17GbzE0SJDkF2GF7JyirAeu5FjWXe0bDcPEL5q7iTgJ8rPwYWrRyCaZr%2BXkN90HbkCVdF0mR77fzmbcPqeLlFuSC1o4AlvZFDVhyMxGF2Xu7YOuJk%2F1e6%2BosWSIdMPl8nlPR9m7xNwD7aDu1AAOVgVwkAF63b0iXOUiGb2cFd2sgw5BAHtAJARsX8JHQhO%2FmfZIEAJ6uGw8ZrR4suxqPCBccteAgTvHp%2Fg%3D%3D; _mzvr=2xO8vjh2hkKQi2_8tVQdng; _mzvs=nn; __utma=79425045.1969782179.1623321540.1623321540.1623321540.1; __utmc=79425045; __utmz=79425045.1623321540.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; _gcl_au=1.1.352373510.1623321540; _fbp=fb.1.1623321540932.1217255371; my-store-code=1215; my-store-name=Peavey%20Mart%20Cornwall; my-store-province=ON; my-store-selected=true; my-store-loaded=true; __utmb=79425045.2.10.1623321540; _mzvt=8_6b6YM0KECV-dpnC6a62w; _mzPc=eyJjb3JyZWxhdGlvbklkIjoiZGUyODA2N2RmYmJjNDEyMGJmOWU0NGFkMWMwNzBjNDciLCJpcEFkZHJlc3MiOiIyYTAyOjJlMDI6YWQ4MDphNDAwOjU4YzU6MWVlOjMxOGE6YTY4NyIsImlzRGVidWdNb2RlIjpmYWxzZSwiaXNDcmF3bGVyIjpmYWxzZSwiaXNNb2JpbGUiOmZhbHNlLCJpc1RhYmxldCI6ZmFsc2UsImlzRGVza3RvcCI6dHJ1ZSwidmlzaXQiOnsidmlzaXRJZCI6IjhfNmI2WU0wS0VDVi1kcG5DNmE2MnciLCJ2aXNpdG9ySWQiOiIyeE84dmpoMmhrS1FpMl84dFZRZG5nIiwiaXNUcmFja2VkIjpmYWxzZSwiaXNVc2VyVHJhY2tlZCI6ZmFsc2V9LCJ1c2VyIjp7ImlzQXV0aGVudGljYXRlZCI6ZmFsc2UsInVzZXJJZCI6IjNjOGJlYzk1Y2M1ODQxMWI4OTFjYzg5MzA5M2M5OTBiIiwiZmlyc3ROYW1lIjoiIiwibGFzdE5hbWUiOiIiLCJlbWFpbCI6IiIsImlzQW5vbnltb3VzIjp0cnVlLCJiZWhhdmlvcnMiOlsxMDE0XSwiaXNTYWxlc1JlcCI6ZmFsc2V9LCJ1c2VyUHJvZmlsZSI6eyJ1c2VySWQiOiIzYzhiZWM5NWNjNTg0MTFiODkxY2M4OTMwOTNjOTkwYiIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWxBZGRyZXNzIjoiIiwidXNlck5hbWUiOiIifSwicHVyY2hhc2VMb2NhdGlvbiI6eyJjb2RlIjoiMTIxNSJ9LCJpc0VkaXRNb2RlIjpmYWxzZSwiaXNBZG1pbk1vZGUiOmZhbHNlLCJub3ciOiIyMDIxLTA2LTEwVDEwOjM5OjIxLjk3Nzc1NThaIiwiY3Jhd2xlckluZm8iOnsiaXNDcmF3bGVyIjpmYWxzZX0sImN1cnJlbmN5UmF0ZUluZm8iOnt9fQ%3D%3D",
        "x-vol-catalog": "1",
        "x-vol-currency": "CAD",
        "x-vol-locale": "en-CA",
        "x-vol-master-catalog": "1",
        "x-vol-site": "49838",
        "x-vol-tenant": "29977",
    }
    response = session.get(start_url, headers=hdr).json()

    all_locations = response["items"]
    for poi in all_locations:
        store_url = "https://www.peaveymart.com/store-details?locationCode={}".format(
            poi["code"]
        )
        location_name = poi["name"].split("-")[0].strip()
        street_address = poi["address"]["address1"]
        if poi["address"].get("address2"):
            street_address += " " + poi["address"]["address2"]
        if poi["address"].get("address3"):
            street_address += " " + poi["address"]["address3"]
        if poi["address"].get("address4"):
            street_address += " " + poi["address"]["address4"]
        street_address = street_address.replace(", Frontier Mall", "")
        city = poi["address"]["cityOrTown"]
        state = poi["address"]["stateOrProvince"]
        zip_code = poi["address"]["postalOrZipCode"]
        country_code = poi["address"]["countryCode"]
        store_number = poi["code"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["locationTypes"][0]["name"]
        latitude = poi["geo"]["lat"]
        longitude = poi["geo"]["lng"]
        hoo = []
        for day, hours in poi["regularHours"].items():
            if day == "timeZone":
                continue
            hoo.append(f'{day} {hours["label"]}')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
            store_url,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
