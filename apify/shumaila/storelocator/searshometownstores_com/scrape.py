import csv
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list


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
    linklist = []
    week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    times = {
        "32400": "9",
        "64800": "6",
        "43200": "12",
        "61200": "5",
        "68400": "7",
        "39600": "11",
        "57600": "4",
        "30600": "8.30",
        "36000": "10",
        "75600": "9",
        "34200": "9:30",
        "46800": "12",
        "45000": "9:30",
        "63000": "5:30",
        "28800": "8",
        "54000": "3",
        "0": "12",
        "50400": "2",
        "66600": "6:30",
        "72000": "8",
        "70200": "7:30",
        "27000": "7:30",
        "73800": "8:30",
        "41400": "11:30",
        "59400": "4:30",
    }
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)
    if True:
        for zip_code in zips:
            search_url = "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/nearby"
            myobj = {
                "city": "",
                "zipCode": str(zip_code),
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
            try:
                loclist = session.post(search_url, json=myobj, headers=headers).json()[
                    "payload"
                ]["nearByStores"]
                if len(loclist) > 0:
                    pass
            except:
                continue
            for loc in loclist:
                title = loc["storeName"]
                street = loc["address"]
                city = loc["city"]
                state = loc["stateCode"]
                pcode = loc["zipCode"]
                phone = loc["phone"]
                phone = "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]
                store = str(loc["unitNumber"])
                link = (
                    "https://www.searshometownstores.com/home/"
                    + state.lower()
                    + "/"
                    + city.lower()
                    + "/"
                    + store.replace("000", "")
                )
                if link in linklist:
                    continue
                linklist.append(link)
                hourlist = loc["storeDetails"]["strHrs"]
                hours = ""
                for day in week:
                    hours = (
                        hours
                        + day
                        + " "
                        + times[hourlist[day]["opn"]]
                        + " AM - "
                        + times[hourlist[day]["cls"]]
                        + " PM "
                    )
                longt = loc["storeDetails"]["longitude"]
                lat = loc["storeDetails"]["latitude"]

                data.append(
                    [
                        "https://www.searshometownstores.com/",
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
