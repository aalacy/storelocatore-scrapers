import csv
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    out = []

    locator_domain = "https://www.anthonyvincenailspa.com"
    api_url = "https://www.anthonyvincenailspa.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-XSRF-TOKEN": "1624701128|6fhhSIyHI7bv",
        "commonConfig": '{"brand":"wix","bsi":"ffdddd58-6ed4-4d4c-9d82-f00f629ecd89|4","consentPolicy":{"essential":true,"functional":true,"analytics":true,"advertising":true,"dataToThirdParty":true},"consentPolicyHeader":{}}',
        "x-wix-site-revision": "2519",
        "Content-Type": "application/json",
        "Origin": "https://www.anthonyvincenailspa.com",
        "Connection": "keep-alive",
        "Referer": "https://www.anthonyvincenailspa.com/_partials/wix-thunderbolt/dist/clientWorker.5ac7b0f5.bundle.min.js",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//option[text()="Choose a location"]/following-sibling::option')

    for d in div:
        state = "".join(d.xpath(".//@value"))

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-XSRF-TOKEN": "1624701128|6fhhSIyHI7bv",
            "commonConfig": '{"brand":"wix","bsi":"ffdddd58-6ed4-4d4c-9d82-f00f629ecd89|4","consentPolicy":{"essential":true,"functional":true,"analytics":true,"advertising":true,"dataToThirdParty":true},"consentPolicyHeader":{}}',
            "x-wix-site-revision": "2519",
            "Content-Type": "application/json",
            "Origin": "https://www.anthonyvincenailspa.com",
            "Connection": "keep-alive",
            "Referer": "https://www.anthonyvincenailspa.com/_partials/wix-thunderbolt/dist/clientWorker.5ac7b0f5.bundle.min.js",
        }

        data = '["Location",{"state":{"$contains":"' + state + '"}},[],0,100,null,null]'
        r = session.post(
            "https://www.anthonyvincenailspa.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax?gridAppId=18aa5821-efbc-4819-8075-f93a54245584&instance=wixcode-pub.328fff89edb80d1d567bbadbba7e76cb5c1548a7.eyJpbnN0YW5jZUlkIjoiMmM5YjYzNjAtZTI0NS00ZWFkLWFiNDktYWVkMGFkYzUwMDdmIiwiaHRtbFNpdGVJZCI6IjU5MzY0NTFkLWIyYzktNDVmNC1hYjYxLTYzOThhYjk4YzUxNCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYyNDcwMTI2MTcxMSwiYWlkIjoiMzc3MTNiOWQtYzVmMy00NGMwLWE3ZTQtMjk5NjRjMjkxNjE0IiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjY5ODJlYjZiLWQyM2YtNDUyMi05YTY1LWU3YTU2ZDU4NzJhNCIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsQWRzRnJlZSxIYXNEb21haW4sSGFzRUNvbW1lcmNlIiwidGVuYW50IjpudWxsLCJzaXRlT3duZXJJZCI6IjY3OGVkMTcxLTA1NDktNDM3OS1hNzBlLWI0ZTdjMWQ5ZTNjOCIsImluc3RhbmNlVHlwZSI6InB1YiIsInNpdGVNZW1iZXJJZCI6bnVsbH0=&viewMode=site",
            headers=headers,
            data=data,
        )
        js = r.json()
        for j in js["result"]["items"]:

            page_url = "https://www.anthonyvincenailspa.com/locations"
            location_name = j.get("f")
            location_type = "<MISSING>"
            street_address = "".join(j.get("address").get("formatted"))
            if street_address.find(",") != -1:
                street_address = street_address.split(",")[0].strip()
            phone = j.get("phoneNumber") or "<MISSING>"
            postal = j.get("zipcode")
            country_code = "US"
            city = j.get("city")
            store_number = "<MISSING>"
            try:
                latitude = j.get("address").get("location").get("latitude")
                longitude = j.get("address").get("location").get("longitude")
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            hours_of_operation = (
                "".join(j.get("operatingHours"))
                .replace("\n", " ")
                .replace("EVERYDAY", "")
                .replace("TEMPORARY HOURS", "")
                .strip()
            )

            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
