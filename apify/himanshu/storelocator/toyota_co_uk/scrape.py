import csv
from sgrequests import SgRequests
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="toyota.co.uk")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    base_url = "https://www.toyota.co.uk/"
    soup = session.get(
        "https://www.toyota.co.uk/api/dealer/drive/-0.1445783/51.502436?count=1000&extraCountries=im|gg|je&isCurrentLocation=false"
    ).json()
    for data in soup["dealers"]:
        street_address1 = ""
        location_name = data["name"]
        street_address1 = data["address"]["address1"].strip()
        if street_address1:
            street_address1 = street_address1
        street_address = street_address1 + " " + data["address"]["address"].strip()
        city = data["address"]["city"]
        zipp = data["address"]["zip"]
        phone = data["phone"]
        state = data["address"]["region"]
        if "Newbridge" in street_address:
            street_address = "2 Lonehead Drive"
            city = "Newbridge"
            state = "Edinburgh"
        lat = data["address"]["geo"]["lat"]
        lng = data["address"]["geo"]["lon"]
        page_url = data["url"]

        temp_hours = data["openingDays"]
        hours = ""
        hours_list = []
        for temp in temp_hours:
            if temp["originalService"] == "ShowRoom":
                day = temp["startDayCode"]
                if temp["endDayCode"] not in day:
                    day = day + "-" + temp["endDayCode"]

                time = temp["hours"][0]["startTime"] + "-" + temp["hours"][0]["endTime"]
                hours_list.append(day + ":" + time)

        if len(hours_list) <= 0:

            for temp in temp_hours:
                if temp["originalService"] == "ShowRoom":
                    day = temp["startDayCode"]
                    if temp["endDayCode"] not in day:
                        day = day + "-" + temp["endDayCode"]

                    time = (
                        temp["hours"][0]["startTime"]
                        + "-"
                        + temp["hours"][0]["endTime"]
                    )
                    hours_list.append(day + ":" + time)
        hours = "; ".join(hours_list).strip()
        if state == "City of Edinburgh":
            state = "Edinburgh"
        if state == "County of Bristol":
            state = "Bristol"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("UK")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

"https://turnersburystedmunds.toyota.co.uk/about-us#anchor-views-opening_hours-block_3"
"http://burystedmunds.toyota.co.uk//about-us#anchor-views-opening_hours-block_3"
