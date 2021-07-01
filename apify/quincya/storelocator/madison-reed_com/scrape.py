import csv
import re

from sgrequests import SgRequests


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

    base_link = "https://www.madison-reed.com/api/colorbar/getLocationsGroupedByRegion"

    headers = {
        "authority": "www.madison-reed.com",
        "method": "GET",
        "path": "/api/colorbar/getAllRegions",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "dig=796ad26b-bb14-4b9a-b3a9-78b5a9721562; dug=a1dbca98-f50e-4b11-b2b0-f0ee0db73d2c; csrf_stp=a73339c1-5ab7-4f42-943f-e390640ca708-ed87ae74-2296-45bc-95f0-c0f04e4a97de; connect.sid=s%3AYFg0YXE5E52W7UGM_zAyGl8wjdehZT1H.ub5TLZZV0A8jM3M%2FIKmtWdwJkRXT95HOC%2FORg5zDPh4; abt_.dOh.Xbg=B; abt_9ZtuSrQg=B; abt_~.7UxQWg=B; abt__qVQU-Eg=B; abt_h09+mrTg=B; _gcl_au=1.1.1385029366.1625129651; FPC=3e9e981c-a7b2-42b3-bf32-711f90f39b93; ajs_anonymous_id=%22796ad26b-bb14-4b9a-b3a9-78b5a9721562%22; _ga=GA1.2.890888777.1625129652; _gid=GA1.2.750707544.1625129652; __pdst=154805a50b1248178a3a851542279758; _wchtbl_uid=69ae9a86-baf7-42ec-a038-5a0395cc8619; _wchtbl_sid=97be332e-d7ba-48a2-8fce-0886c78f66ef; _fbp=fb.1.1625129652510.1928015521; _hjTLDTest=1; _hjid=dce80acd-de2a-45a1-94c8-9637ff81f309; _hjFirstSeen=1; _wchtbl_do_not_process=0; _wchtbl_pixel_sync=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; __adroll_fpc=55dea3adce05092dd41dd79f63c72f7f-1625129653348; _li_dcdm_c=.madison-reed.com; _lc2_fpi=12513cfe94e6--01f9gmd59ts1f14zbtwt7767av; extole_access_token=B9VABEHR6P9FCLVRCH2M40EKFU; __ssid=5276d14907a50260a611ed6f17dfc2c; no_email_capture_modal=true; ajs_user_id=null; cartType=active; cic=0; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jul+01+2021+05%3A54%3A17+GMT-0400+(Atlantic+Standard+Time)&version=6.2.0&landingPath=NotLandingPage&groups=C0003%3A1%2CC0001%3A1%2CC0002%3A0%2CC0004%3A0%2CBG1%3A0&hosts=&legInt=&AwaitingReconsent=false; __ar_v4=FMABVAFZDZD6ZC7WSVLYTE%3A20210631%3A14%7CQGMX6GGPXNATZDJSRGCS4N%3A20210631%3A14%7CKQ5MCZ3KBNE53A7HPYF6RC%3A20210631%3A14",
        "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "pragma": "no-cache",
        "referer": "https://www.madison-reed.com/colorbar/locations",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "if-none-match": 'W/"55f5-DOSwuk5trDJYUYAacvJrrbT/o/Q"',
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "x-csrf-stp": "a73339c1-5ab7-4f42-943f-e390640ca708-ed87ae74-2296-45bc-95f0-c0f04e4a97de",
    }

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()[0]

    data = []
    locator_domain = "madison-reed.com"

    for state in stores:
        state_stores = stores[state]
        for store in state_stores:
            opened = store["hasOpened"]
            if not opened:
                continue
            location_name = store["neighborhood"]
            street_address = store["address1"].strip()
            if not street_address[:1].isnumeric():
                street_address = store["address2"].strip()
            city = store["city"].strip()
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["_id"]
            location_type = "<MISSING>"
            phone = store["phone"]
            hours = store["hours"]
            hours_of_operation = ""
            for row in hours:
                day = row["day"]
                closed = row["closed"]
                if closed:
                    hours_of_operation = hours_of_operation + " " + day + " Closed"
                else:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + day
                        + " "
                        + row["open"]
                        + "-"
                        + row["close"]
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
            latitude = store["coordinates"]["lat"]
            longitude = store["coordinates"]["lon"]
            link = "https://www.madison-reed.com/colorbar/locations/" + store["code"]
            # Store data
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
