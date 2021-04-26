import req
import json
import csv


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
    locator_domain = "https://www.christiedental.com/"
    missingString = "<MISSING>"

    def send(l, d):
        return req.Req().post(l, data=d)

    def toJSON(o):
        return json.loads(o.text)

    def allStores():
        l = send(
            "https://www.christiedental.com/wp-admin/admin-ajax.php",
            {
                "action": "prov_search",
                "data[search_type]": "all",
                "data[lat]": "28.5383",
                "data[lng]": "-81.3792",
                "data[sort_field]": "dentist_last",
                "data[sort_order]": "ASC",
            },
        )
        return toJSON(l)["results"]

    s = allStores()
    result = []

    def validatorCheck(s):
        if s == "" or not s:
            return missingString
        else:
            return s

    for ss in s:
        url = validatorCheck(ss["website"])
        name = validatorCheck(ss["name"])
        street = validatorCheck(ss["address1"] + " " + ss["address2"])
        city = validatorCheck(ss["city"])
        country = validatorCheck(ss["country"])
        num = validatorCheck(ss["id"])
        lat = validatorCheck(ss["lat"])
        lng = validatorCheck(ss["lng"])
        zp = validatorCheck(ss["postal_code"])
        phone = validatorCheck(ss["phone_primary"])
        state = validatorCheck(ss["state"])
        timeArray = []
        for d in ss["hours"]:
            h = list(filter(None, ss["hours"][d]))
            if not h:
                pass
            else:
                timeArray.append(
                    d + " : " + ss["hours"][d][0] + " - " + ss["hours"][d][1]
                )
        hours = validatorCheck(", ".join(timeArray).strip())
        result.append(
            [
                locator_domain,
                url,
                name,
                street,
                city,
                state,
                zp,
                country,
                num,
                phone,
                missingString,
                lat,
                lng,
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
