import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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

    session = SgRequests()

    data = []
    found_poi = []

    locator_domain = "morganstanley.com"

    max_results = 600
    max_distance = 2500

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for postcode in search:
        base_link = (
            "https://advisor.morganstanley.com/search?profile=16348&q=%s&r=%s"
            % (postcode, max_distance)
        )

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "_ga=GA1.2.1715091287.1607033108; _gcl_au=1.1.641902187.1607033109; s_ecid=MCMID%7C07966173389439194212973425362289259424; s_visit=1; mbox=PC#114da96745994d3080f7cd7cab228fa4.34_0#1670278260|session#c1e67ffdef3c4a8cbf860bac45f75010#1607483569; s_vnum=1609473600496%26vn%3D2; s_newRepeat=1607481714492-Repeat; s_daysSince=1607481714494; s_ev90=%5B%5B%27Other%2520Campaigns%27%2C%271607481708676%27%5D%2C%5B%27Typed%2FBookmarked%27%2C%271607481714081%27%5D%2C%5B%27Typed%2FBookmarked%27%2C%271607481714128%27%5D%2C%5B%27Typed%2FBookmarked%27%2C%271607481714171%27%5D%2C%5B%27Typed%2FBookmarked%27%2C%271607481714517%27%5D%5D; _uetvid=6e938d4035b411eb8fff7d6f128ec755; s_vnum=1609473600496%26vn%3D3; _gid=GA1.2.1196576015.1608260906; AMCVS_9355F0CC5405D58C0A4C98A1%40AdobeOrg=1; AMCV_9355F0CC5405D58C0A4C98A1%40AdobeOrg=-1303530583%7CMCIDTS%7C18615%7CMCMID%7C07966173389439194212973425362289259424%7CMCAAMLH-1608865708%7C7%7CMCAAMB-1608865708%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1608268108s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-18607%7CvVersion%7C3.3.0%7CMCCIDH%7C-718314888; ak_bmsc=0298507318391DDE578FA86479F6DAEF17CEC12FCE5D0000291DDC5F4AE13829~plD3tKlj9P8SIy2Gn4wiNeFANN1UL5BhsN5+5XofWHfDk1jc1spyr1fPIs6E+anolT9y2YC9LyxBemJt2EkHJjqWqBktv4tKIBGZ9YnzAk3M/fjXToar/SEdna/2gBNdYHsSuEAaLA56Uxy+K2LpePon3tGgInKKxxbUdM8ewk46a3FTUNMCDwvUrWXZFZJZdyhwXjOcWCSxmsFf+lFnI4faYrMnsNuz0Rd/Q2VRHT37+vrE2p4/HIFB7HY2J5Aq2q; s_invisit=true; s_daysSince_s=More%20than%207%20days; s_ppn=wealth%20management%20%7C%20find%20a%20financial%20advisor; s_cc=true; bm_sv=9B85756C38F0949FCC614305FBB95E99~Vu3x0kOCbp5P874q9xtxdtFK9V9JRjPqz4bci+p4lP4ifZliH3BXiPf5mnhshtuQLxyq9azMMX2eD/vp1R5rpHuhqvm5M+1ogM7LGy9xv4VouBhlXpm8/lHrOZYzEJJoHRaLQ94iSMqR/ZO16JitJpb8/Oy/Ib1A5bvkFMq6OBI=; _gat_yext=1; s_getNewRepeat=1608261363511-Repeat; s_daysSince=1608261363513",
            "Host": "advisor.morganstanley.com",
            "Origin": "https://cbna.com",
            "Referer": "https://advisor.morganstanley.com/search?profile=%s&q=19125&r=%s"
            % (postcode, max_distance),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        }

        log.info(base_link)
        req = session.get(base_link, headers=headers).json()
        stores = req["response"]["entities"]
        count = req["response"]["count"]

        total = int(count / 10) + (count % 10 > 0)
        for page_num in range(1, total + 1):

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
                if not link:
                    link = "<MISSING>"

                search.mark_found([latitude, longitude])

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

            offset = page_num * 10
            next_link = base_link + "&offset=" + str(offset)
            log.info(next_link)
            stores = session.get(next_link, headers=headers).json()["response"][
                "entities"
            ]

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
