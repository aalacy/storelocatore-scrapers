import csv
import sgrequests
import re


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
    locator_domain = "https://interlinksupply.com/"
    missingString = "<MISSING>"

    def retrieveAllStores():
        api = (
            sgrequests.SgRequests()
            .get(
                "https://interlinksupply.com/locations",
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                },
            )
            .text
        )
        res = []
        storevar = re.findall(r"var store_(.*?)=", api)
        for el in storevar:
            latlng = (
                re.search(r"var store_{el}=(.*?);".format(el=el), api)
                .group(1)
                .replace("new google.maps.LatLng(", "")
                .replace(")", "")
                .split(",")
            )
            content = (
                re.search(r"(?ss)var infowindow_{el} = (.*?);".format(el=el), api)
                .group(1)
                .replace("new google.maps.InfoWindow({", "")
                .replace("})", "")
                .replace('content:"', "")
                .strip()[:-1]
                .split("<br>")
            )
            name = content[0]
            street = content[1]
            city = content[2].split(",")[0]
            if "Suite" in content[2] or "#" in content[2]:
                street = content[1] + " " + content[2]
                city = content[3].split(",")[0]
                state = content[3].split(",")[1].strip().split(" ")[-2]
                zp = content[3].split(",")[1].strip().split(" ")[-1]
            else:
                state = content[2].split(",")[1].strip().split(" ")[-2]
                zp = content[2].split(",")[1].strip().split(" ")[-1]
            lat = latlng[0]
            lng = latlng[1]
            store_num = el
            phone = content[-1].replace("x22", "")
            res.append(
                {
                    "locator_domain": locator_domain,
                    "page_url": missingString,
                    "location_name": name,
                    "street_address": street,
                    "city": city,
                    "state": state,
                    "zip": zp,
                    "country_code": missingString,
                    "store_number": store_num,
                    "phone": phone,
                    "location_type": missingString,
                    "latitude": lat,
                    "longitude": lng,
                    "hours": missingString,
                }
            )
        return res

    result = []

    for s in retrieveAllStores():
        result.append(
            [
                s["locator_domain"],
                s["page_url"],
                s["location_name"],
                s["street_address"],
                s["city"],
                s["state"],
                s["zip"],
                s["country_code"],
                s["store_number"],
                s["phone"],
                s["location_type"],
                s["latitude"],
                s["longitude"],
                s["hours"],
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
