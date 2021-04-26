import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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
    base_url = "http://pancho-villas.com/locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []

    k = soup.find("div", {"id": "content"}).find_all(
        class_="vc_column_container col-md-4"
    )

    for j in k:
        tem_var = []

        phone = j.a.text.replace("CALL", "").strip()
        city = j.find_all("p")[-1].text.split(",")[1].strip()
        state = j.find_all("p")[-1].text.split(",")[2].split()[0]
        zipcode = j.find_all("p")[-1].text.split(",")[2].split()[1]
        st = j.find_all("p")[-1].text.split(",")[0].strip()
        name = "PV's " + city
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        tem_var.append("http://pancho-villas.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        tem_var.append(base_url)
        return_main_object.append(tem_var)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
