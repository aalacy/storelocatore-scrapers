import csv
from sgrequests import SgRequests

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
}


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
    data = []
    storelist = []

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for statenow in states:
        url = (
            "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/getStoreDetailsByState?state="
            + statenow
        )
        loclist = session.get(url, headers=headers).json()["payload"]["stores"]

        for loc in loclist:
            title = loc["storeName"]
            pcode = loc["zipCode"]
            city = loc["city"]
            state = loc["stateCode"]
            street = loc["streetAddress"]
            phone = loc["phoneNumber"]
            hours = (
                "Mon "
                + loc["monHrs"]
                + " Tue "
                + loc["tueHrs"]
                + " Wed "
                + loc["wedHrs"]
                + " Thu "
                + loc["thrHrs"]
                + " Fri "
                + loc["friHrs"]
                + " Sat "
                + loc["satHrs"]
                + " Sun "
                + loc["sunHrs"]
            )
            search_url = "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/nearby"
            myobj = {
                "city": "",
                "zipCode": str(pcode),
                "searchType": "",
                "state": "",
                "session": {
                    "sessionKey": "",
                    "trackingKey": "",
                    "appId": "MYGOFER",
                    "guid": 0,
                    "emailId": "",
                    "userRole": "",
                    "userId": 0,
                },
                "security": {"authToken": "", "ts": "", "src": ""},
            }
            lat = longt = store = link = "<MISSING>"

            locnow = session.post(search_url, json=myobj, headers=headers).json()[
                "payload"
            ]["nearByStores"]

            for div in locnow:
                if (
                    city.upper() + " - AUTH HOMETOWN" == div["storeName"]
                    or phone.replace("(", "")
                    .replace(")", "")
                    .replace("-", "")
                    .replace(" ", "")
                    .replace(".", "")
                    == div["phone"]
                ):  # street.lower().replace('.','').replace(',','').strip() == div["address"].lower().replace('.','').replace(',','').strip():
                    store = str(div["unitNumber"])
                    link = (
                        "https://www.searshomeapplianceshowroom.com/home/"
                        + state.lower()
                        + "/"
                        + city.lower()
                        + "/"
                        + store.replace("000", "")
                    )
                    longt = div["storeDetails"]["longitude"]
                    lat = div["storeDetails"]["latitude"]
                    break
            if phone in storelist:
                continue
            storelist.append(phone)
            data.append(
                [
                    "https://www.searshomeapplianceshowroom.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
    return data


def scrape():

    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
