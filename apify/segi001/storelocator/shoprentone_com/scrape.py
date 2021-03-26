import csv
from sgrequests import SgRequests
import json


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
    locator_domain = "https://shoprentone.com/"
    api = "https://shoprentone.com/api/v1/locations/"
    missingString = "<MISSING>"

    s = SgRequests()

    apiData = json.loads(s.post(api).text)

    result = []

    for el in apiData["locations"]:
        meta = json.loads(
            el["meta_tags"]
            .strip()
            .replace('<script type="application/ld+json">', "")
            .replace("</script>", "")
            .replace("```", "")
            .replace(": ,", ': "",')
        )
        tArray = []
        for day in meta["openingHoursSpecification"][0]["dayOfWeek"]:
            tArray.append(
                [
                    day,
                    meta["openingHoursSpecification"][0]["opens"],
                    meta["openingHoursSpecification"][0]["closes"],
                ]
            )

        if meta["openingHoursSpecification"][1]["dayOfWeek"] != "":
            tArray.append(
                [
                    meta["openingHoursSpecification"][1]["dayOfWeek"],
                    meta["openingHoursSpecification"][1]["opens"],
                    meta["openingHoursSpecification"][1]["closes"],
                ]
            )
        hours = ", ".join(
            str(x)
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(",", ":", 1)
            .replace(",", " -", 2)
            for x in tArray
        )
        store_page = el["slug"].strip()
        result.append(
            [
                locator_domain,
                "{}{}".format(locator_domain + "locations/", store_page),
                el["name"],
                el["address"],
                el["city"].replace(" IL", ""),
                el["state"],
                el["zipcode"],
                missingString,
                el["store_number"],
                el["phone_number"],
                missingString,
                el["latitude"],
                el["longitude"],
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
