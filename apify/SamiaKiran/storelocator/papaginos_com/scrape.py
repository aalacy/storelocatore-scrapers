import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "authority": "api.papaginos.com",
    "method": "GET",
    "path": "/api/v2/locations",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer EXhe9xc8Pa--s-y96YStIHXvAIPVg7zIlN0QvPsjW1w4p4BfgEdaqjIElVyyZGS7xAerIZ22E_FE8HUkUqyihdj3NfIhFUHIr-sQfYUMv3tvw6bu536mV13fvu4xskprtqe4X-VAzHgmQ5lFvwEH-iA_mghwYN5x5ulZfWbrfpEiuq9sz_A2gxqKr45EibHtYlE4kP1Rzhbig7hCZt6dsF1g420EW2JEAE2XumSt1Uj-cfElJ7npwuXSCQ0wOooWaboadmNif5g4ctLX4phgtBl4s76c-rwEjHYG-rWXjp5QNrZPcAfptoXcF0v8yH_TMAUgHZsZbYRFodiO3P8p4vhYQYlNjdGmO0CUblDSzulrEpcgYKSCb621CCh5rLfCyWqzHsG1rMre6swV6W0rhY7IQZlu3_7Ygv7jRMViEfC7-k7M-D34wI1SlWiy3DTJBojV4xQ_PJg7LSHp3ckIIdb3aS0TVKy0AtZ9pvwu7auioYCarwTMjU5wn-PchO1v5AV01mdmp-VdhYG5YWhKjCtX_bS6qfxghubpJn8Oj2FDqIvf",
    "origin": "https://www.papaginos.com",
    "referer": "https://www.papaginos.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
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
    # Your scraper here
    data = []
    url = "https://api.papaginos.com/api/v2/locations"

    r = session.get(url, headers=headers, verify=False)
    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc["name"]
        store = loc["number"]
        sublink = "https://www.papaginos.com/" + str(store)

        lat = loc["latitude"]
        longt = loc["longitude"]
        if loc["address2"]:
            street = loc["address1"] + " " + loc["address2"]
        else:
            street = loc["address1"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        ccode = "USA"
        store_type = "<MISSING>"
        phone = loc["phone"]
        if title == "":
            title = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if longt == "":
            longt = "<MISSING>"
        if street == "":
            street = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if pcode == "":
            pcode = "<MISSING>"
        if ccode == "":
            ccode = "USA"
        if store_type == "":
            store_type = "<MISSING>"
        hours_of_operation = ""
        for k in loc["storehours"]:
            hours_of_operation = hours_of_operation + k["days"] + " " + k["times"]
        data.append(
            [
                "https://www.papaginos.com",
                sublink,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                store_type,
                lat,
                longt,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
