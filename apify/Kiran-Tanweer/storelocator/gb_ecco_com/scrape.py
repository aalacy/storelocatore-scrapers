import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import itertools as it

logger = SgLogSetup().get_logger("gb_ecco_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    for i in it.chain(
        range(11906, 12937),
        range(34489, 37068),
        range(40646, 46070),
        range(52508, 56381),
    ):

        count = str(i)
        url = "https://gb.ecco.com/api/store/finder/00010" + count
        stores_req = session.get(url, headers=headers).json()
        if stores_req is not None:
            storetype = stores_req["StoreType"].strip()
            if storetype == "ECCO":
                country = stores_req["CountryCode"].strip()
                if country == "GB":
                    storeid = stores_req["StoreId"]
                    title = stores_req["Name"]
                    street = stores_req["Street"]
                    city = stores_req["City"]
                    pcode = stores_req["PostalCode"]
                    state = "<MISSING>"
                    phone = stores_req["Phone"]
                    lat = stores_req["Latitude"]
                    lng = stores_req["Longitude"]
                    mon_start = stores_req["MondayOpen"]
                    tue_start = stores_req["TuesdayOpen"]
                    wed_start = stores_req["WednesdayOpen"]
                    thu_start = stores_req["ThursdayOpen"]
                    fri_start = stores_req["FridayOpen"]
                    sat_start = stores_req["SaturdayOpen"]
                    sun_start = stores_req["SundayOpen"]
                    mon_close = stores_req["MondayClose"]
                    tue_close = stores_req["TuesdayClose"]
                    wed_close = stores_req["WednesdayClose"]
                    thu_close = stores_req["ThursdayClose"]
                    fri_close = stores_req["FridayClose"]
                    sat_close = stores_req["SaturdayClose"]
                    sun_close = stores_req["SundayClose"]
                    mon = "Monday: " + mon_start + "-" + mon_close
                    tue = "Tuesday: " + tue_start + "-" + tue_close
                    wed = "Wednesday: " + wed_start + "-" + wed_close
                    thu = "Thursday: " + thu_start + "-" + thu_close
                    fri = "Friday: " + fri_start + "-" + fri_close
                    sat = "Saturday: " + sat_start + "-" + sat_close
                    sun = "Sunday: " + sun_start + "-" + sun_close
                    hoo = (
                        mon
                        + " "
                        + tue
                        + " "
                        + wed
                        + " "
                        + thu
                        + " "
                        + fri
                        + " "
                        + sat
                        + " "
                        + sun
                    )

                    if lat == 0.0:
                        lat = "<MISSING>"
                    if lng == 0.0:
                        lng = "<MISSING>"
                    if phone is None:
                        phone = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if title.find("/") != -1:
                        title = title.split("/")[0].strip()
                    hoo = hoo.strip()

                    if (
                        hoo
                        == "Monday: - Tuesday: - Wednesday: - Thursday: - Friday: - Saturday: - Sunday: -"
                    ):
                        hoo = "<MISSING>"

                    if street == "20 Castle Lane":
                        temp = city
                        city = pcode
                        pcode = temp

                    data.append(
                        [
                            "https://gb.ecco.com/",
                            "https://gb.ecco.com/en-GB/CustomerCare/StoreFinder",
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            "UK",
                            storeid,
                            phone,
                            storetype,
                            lat,
                            lng,
                            hoo,
                        ]
                    )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
