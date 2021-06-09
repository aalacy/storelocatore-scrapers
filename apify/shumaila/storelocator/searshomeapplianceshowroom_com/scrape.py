import csv
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sglogging import SgLogSetup
import time


logger = SgLogSetup().get_logger("searshomeapplianceshowroom_com")
MISSING = "<MISSING>"
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


def fetch_data():
    data = []
    linklist = []
    week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)
    for zcnum, zip_code in enumerate(zips):
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
            r = session.post(search_url, json=myobj, headers=headers)
        except:
            logger.info("Let it sleep for 10 seconds")
            time.sleep(10)
            logger.info("Sleeping done")
            r = session.post(search_url, json=myobj, headers=headers)
        loclist_main = r.json()
        if "payload" in loclist_main:
            r_payload = loclist_main["payload"]
            if "nearByStores" in r_payload:
                logger.info("NearByStores Key Found in Payload!!")
                r_nearbystores = r_payload["nearByStores"]
                if r_nearbystores is None:
                    continue
                else:
                    loclist = loclist_main["payload"]["nearByStores"]
                    logger.info(
                        "POST Response data contains store Data, Awesome! Let's parse it!!!"
                    )
                    logger.info(f"Pulling the data from zipcode [{zcnum}: {zip_code}]")
                    for loc in loclist:
                        title = loc["storeName"] or MISSING
                        logger.info(f"Location Name: {title}")
                        street = loc["address"] or MISSING
                        city = loc["city"] or MISSING
                        state = loc["stateCode"] or MISSING
                        pcode = loc["zipCode"] or MISSING
                        phone = loc["phone"] or MISSING
                        phone = "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]
                        store = str(loc["unitNumber"]) or MISSING
                        link = (
                            "https://www.searshomeapplianceshowroom.com/home/"
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
                        longt = loc["storeDetails"]["longitude"] or MISSING
                        lat = loc["storeDetails"]["latitude"] or MISSING
                        if len(phone) < 5:
                            phone = MISSING
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

    logger.info("Scraping Started")
    data = fetch_data()
    write_output(data)
    logger.info(f"Total stores processed: {len(data)}")


if __name__ == "__main__":
    scrape()
