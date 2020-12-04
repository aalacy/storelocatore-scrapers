import csv

from sglogging import sglog

from sgrequests import SgRequests

import sgzip

from sgzip import SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="morganstanley.com")


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

    max_results = 10
    max_distance = 100

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "_ga=GA1.2.1715091287.1607033108; _gid=GA1.2.1384453119.1607033108; _gcl_au=1.1.641902187.1607033109; AMCVS_9355F0CC5405D58C0A4C98A1%40AdobeOrg=1; s_ecid=MCMID%7C07966173389439194212973425362289259424; s_cc=true; check=true; mbox=session#114da96745994d3080f7cd7cab228fa4#1607035320|PC#114da96745994d3080f7cd7cab228fa4.34_0#1670278260; _uetsid=6e933c0035b411eb983bd1c848ac214a; _uetvid=6e938d4035b411eb8fff7d6f128ec755; s_ppvl=Site%2520Map%2C99%2C19%2C6602%2C1855%2C984%2C1920%2C1080%2C1%2CP; s_ppv=Site%2520Map%2C99%2C99%2C6602%2C1855%2C984%2C1920%2C1080%2C1%2CP; s_visit=1; s_newRepeat=1607033472495-New; s_vnum=1609473600496%26vn%3D1; s_daysSince=1607033472498; s_ev90=%5B%5B%27Natural%2520Search%27%2C%271607033472500%27%5D%5D; AMCV_9355F0CC5405D58C0A4C98A1%40AdobeOrg=-1303530583%7CMCIDTS%7C18600%7CMCMID%7C07966173389439194212973425362289259424%7CMCAAMLH-1607650571%7C7%7CMCAAMB-1607650571%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1607052971s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-18607%7CvVersion%7C3.3.0%7CMCCIDH%7C-718314888; s_vnum=1609473600496%26vn%3D2; s_invisit=true; s_daysSince_s=Less%20than%201%20day; bm_mi=95EFEF77011A45224ADAE8BE9022F939~dh6BK6zYOJPp1M+uvhA8Re8GQY0TMcgSRmzcbwaR0AHJe5I295Fehdoc+Lrv9ZOpHtufeg9SbURKNWHkJSCnnFT60BJbnLN5CfFh4fVFDZfvzlyqB1n5MCfy7RnQBvprcYAnhREUas9UK0UYsUpZ0R9MJWfLQN24Y8hNo94+dIcI5OUTfizDySo6d0wCXGgunVD9VEmEucAGVlWJrcIJcm8J6nkGC5zKko4bsKbv7a/YVLeBgkyzLIbDQaQu6P7U; ak_bmsc=B1FBE9CEB1174CF143CB476930E89B49686B3D458D250000DA9FC95FFCC8285C~plGpWjCYa59MA+uWicAF3IgPyNJbYLLfO2hA4RGM4bv/b2PA3hFdTzTdMQU9qDVIhsXHGB90s8clfvLzxeJkuVVqzDdMBNWRMiRzHbBqF54KdOBtjEIDdhwzai4xmH9WgsevSsC/5WHCOAfCzNrplfiPtF7gbDiM6MgYXu4ckGbT+kADH8seYrulRIVo/aBrvi3UuBo/nFl+VtzxexckofGjcxmDWDMsEbj3+kAVtLbdnD3aKCb3WpVCc2bBqwKWNj; s_ppn=wealth%20management%20%7C%20find%20a%20financial%20advisor; s_getNewRepeat=1607050232027-Repeat; s_daysSince=1607050232031; _gat_yext=1; bm_sv=8041CA1849CC0ABCA9D564263CCFBE18~bVRDyWG3RZ7p7xuc1S5QZQH+wroo/N5gQBJcHoQ5PmrTM0q2Qmsgz8LyucvE86/nreK9TgIuZbmCJfwcgASjqD207DXiWut7Yr0mMPtU+mYa2IPs/Md7rRV2PhxrzZOT0WvCUvl1hUVktwtEtihCM9/GYdGZBprp+nrVZxKDpm8=",
        "Host": "advisor.morganstanley.com",
        "Origin": "https://cbna.com",
        "Referer": "https://advisor.morganstanley.com/search?profile=16348&q=19125&r=%s"
        % (max_distance),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    session = SgRequests()

    data = []
    found_poi = []

    locator_domain = "morganstanley.com"

    search = sgzip.DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    search.initialize()
    postcode = search.next()

    while postcode:
        print(postcode)
        base_link = (
            "https://advisor.morganstanley.com/search?profile=16348&q=%s&r=%s"
            % (postcode, max_distance)
        )

        for i in range(100):
        stores = session.get(base_link, headers=headers).json()["response"]["entities"]

        result_coords = []

        for i in stores:
            store = i["profile"]

            try:
                street_address = (
                    store["address"]["line1"] + " " + store["address"]["line2"]
                ).strip()
            except TypeError:
                street_address = store["address"]["line1"].strip()
            city = store["address"]["city"]
            location_name = "Morgan Stanley " + city + " Branch"
            state = store["address"]["region"]
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["countryCode"]
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = store["mainPhone"]["display"]

            street_city = street_address + city
            if street_city in found_poi:
                continue
            found_poi.append(street_city)

            hours_of_operation = "<MISSING>"
            latitude = store["yextDisplayCoordinate"]["lat"]
            longitude = store["yextDisplayCoordinate"]["long"]

            try:
                link = store["websiteUrl"]
            except KeyError:
                link = "<MISSING>"

            result_coords.append([latitude, longitude])
            search.update_with(result_coords)

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

        if len(result_coords) > 0:
            search.update_with(result_coords)
        postcode = search.next()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
