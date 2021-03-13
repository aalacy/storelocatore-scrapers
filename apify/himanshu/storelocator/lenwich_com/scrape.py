import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "http://lenwich.com/location/"
    r = session.get(base_url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    store_detail = []
    store_name = []

    info = soup.find_all("div", {"class": "locations-info"})
    for i in info:
        tem_var = []
        data = list(i.stripped_strings)
        name = data[0].encode("ascii", "ignore").decode("ascii").strip()
        store_name.append(name.encode("ascii", "ignore").decode("ascii").strip())
        hours = ""
        if len(data) == 7:
            if "Mon – Fri : 6am – 8pm" in data[4]:
                hours = data[4] + " " + data[5] + " " + data[6]
            else:
                hours = hours + data[5] + " " + data[6]
        elif len(data) == 8:
            hours = hours + data[5] + " " + data[6] + " " + data[7]
        elif len(data) == 9:
            hours = hours + data[5] + " " + data[6] + " " + data[7] + " " + data[8]

        elif len(data) == 6:
            hours = hours + data[4] + " " + data[5]
        try:
            a = i.find("a", class_="restaurants-buttons")["href"].strip()
            store_number = "<MISSING>"
            r_loc = session.get(a)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            details = list(soup_loc.find("div", class_="footer_two").stripped_strings)
            details = [el.replace("\x95", " ") for el in details]
            street_address = details[0].split("\n")[1].strip()
            city = details[0].split("\n")[-1].split(",")[0].strip()
            state = details[0].split("\n")[-1].split(",")[1].split()[0].strip()
            zipp = details[0].split("\n")[-1].split(",")[1].split()[-1].strip()
            phone = details[-2].strip()
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp)
            tem_var.append("US")
            tem_var.append(store_number)
            tem_var.append(phone.replace("302 Columbus Ave", ""))
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours.replace("Order", "").strip())
            tem_var.append(a)
            tem_var = [
                str(x).encode("ascii", "ignore").decode("ascii").strip()
                if x
                else "<MISSING>"
                for x in tem_var
            ]
            store_detail.append(tem_var)
        except:
            details = data
            a = "<MISSING>"
            store_number = "<MISSING>"
            street_address = details[1].strip()
            city = details[2].strip().split(",")[0].strip()
            state = details[2].strip().split(",")[-1].strip().split(" ")[0].strip()
            if not state.isalpha():
                state = "<MISSING>"
            zipp = details[2].strip().split(",")[-1].strip().split(" ")[-1].strip()
            phone = "<MISSING>"
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp)
            tem_var.append("US")
            tem_var.append(store_number)
            tem_var.append(phone.replace("302 Columbus Ave", ""))
            tem_var.append(details[-1].strip())
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            tem_var.append(a)
            tem_var = [
                str(x).encode("ascii", "ignore").decode("ascii").strip()
                if x
                else "<MISSING>"
                for x in tem_var
            ]
            store_detail.append(tem_var)
            pass

    for i in range(len(store_name)):
        store = list()
        store.append("http://lenwich.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
