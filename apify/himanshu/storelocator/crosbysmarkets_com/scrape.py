import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    url = [
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJT36uAoYU44kRAWehb-73w8M&17m1&2e1&callback=_xdc_._8l83hw&client=google-maps-pro&token=55661",
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJkVtpuAcV44kRUVt_osaK9_U&17m1&2e1&callback=_xdc_._w42qx5&client=google-maps-pro&token=9152",
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJuY3XjgM944kR1EjqU7q3A9U&17m1&2e1&callback=_xdc_._77qt7b&client=google-maps-pro&token=77567",
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJ55Y_F0Ka44kRdWTtD-CB_Dc&17m1&2e1&callback=_xdc_._633r9j&client=google-maps-pro&token=73803",
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJw1u3bW4X44kRwFCjPQKr4k0&17m1&2e1&callback=_xdc_._ldj3u6&client=google-maps-pro&token=129714",
        "https://maps.googleapis.com/maps/api/place/js/PlaceService.GetPlaceDetails?2sen-GB&6e13&10e3&14m1&1sChIJAVU6xlcb44kRLlh7dFe9y8o&17m1&2e1&callback=_xdc_._go7bgc&client=google-maps-pro&token=20327",
    ]
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }
    for u in url:
        r = session.get(u, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        jd = json.loads(
            str(soup).split('"result" :')[1].split('"status"')[0].strip().rstrip(",")
        )
        location_name = jd["name"]
        addr = jd["formatted_address"].split(",")
        street_address = addr[0]
        city = addr[1].split("-")[0]
        state = addr[2].strip().split(" ")[0]
        zipp = addr[2].strip().split(" ")[1]
        phone = jd["formatted_phone_number"]
        latitude = jd["geometry"]["location"]["lat"]
        longitude = jd["geometry"]["location"]["lng"]
        hours_of_operation = ", ".join(jd["opening_hours"]["weekday_text"])
        store = []
        store.append("http://www.crosbysmarkets.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append("<MISSING>")
        store = [
            x.encode("ascii", "ignore").decode("ascii").strip() if type(x) == str else x
            for x in store
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
