import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
    base_url = "http://www.batterysource.com/find_store.php"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")
    return_main_object = []
    data = soup.find_all("div", {"class": "address_block"})

    for d in data:
        tem_var = []
        name = list(d.stripped_strings)[0]
        st = list(d.stripped_strings)[1]
        if st == "Coming Soon" or st == "New Store":
            st = list(d.stripped_strings)[2]
            city = list(d.stripped_strings)[3].split(",")[0]
            if list(d.stripped_strings)[3].find(",") != -1:
                state = list(d.stripped_strings)[3].split(",")[1].split(" ")[1]
            else:
                state = "<MISSING>"
            if list(d.stripped_strings)[3].find(",") != -1:
                zip1 = list(d.stripped_strings)[3].split(",")[1].split(" ")[2]
            else:
                zip1 = "<MISSING>"
            phone = list(d.stripped_strings)[4].replace("Now Open!", "")
            hours = list(d.stripped_strings)[5]

            if phone.find("Mon") != -1:
                hours = phone
                phone = "<MISSING>"
        else:
            city = list(d.stripped_strings)[2].split(",")[0]
            if list(d.stripped_strings)[2].find(",") != -1:
                state = list(d.stripped_strings)[2].split(",")[1].split(" ")[1]
            else:
                state = "<MISSING>"
            if list(d.stripped_strings)[2].find(",") != -1:
                zip1 = list(d.stripped_strings)[2].split(",")[1].split(" ")[2]
            else:
                zip1 = "<MISSING>"
            phone = list(d.stripped_strings)[3].replace("Now Open!", "")
            hours = list(d.stripped_strings)[4]
            if phone.find("Mon") != -1:
                hours = phone
                phone = "<MISSING>"
        tem_var.append("https://www.batterysource.com")
        tem_var.append("https://www.batterysource.com/find_store.php")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("batterysource")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
