import csv
import sgrequests
import json


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8") as output_file:
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
    locator_domain = "https://www.levi.com/GB/en_GB"

    missingString = "<MISSING>"

    api = "https://www.levi.com/nextgen-webhooks/?operationName=storeDirectory&locale=GB-en_GB"

    result = []

    data = {
        "operationName": "storeDirectory",
        "query": "query storeDirectory($countryIsoCode: String!) {  storeDirectory(countryIsoCode: $countryIsoCode) {    storeFinderData {      addLine1      addLine2      city      country      departments      distance      hrsOfOperation {        daysShort        hours        isOpen      }      latitude      longitude      mapUrl      phone      postcode      state      storeId      storeName      storeType      todaysHrsOfOperation {        daysShort        hours        isOpen      }      uom    }  }}",
        "variables": {"countryIsoCode": "GB"},
    }
    d = json.loads(sgrequests.SgRequests().post(api, json=data).text)["data"][
        "storeDirectory"
    ]["storeFinderData"]
    for e in d:
        name = e["storeName"].replace('"', "'")
        street = e["addLine1"]
        if e["addLine2"]:
            street = e["addLine1"] + " " + e["addLine2"]
        city = e["city"]
        country = e["country"]
        phone = e["phone"]
        zp = e["postcode"]
        if not zp:
            zp = missingString
        if not phone:
            phone = missingString
        state = missingString
        if e["state"]:
            state = e["state"]
        typ = e["storeType"]
        storenum = e["storeId"]
        lat = e["latitude"]
        lng = e["longitude"]
        timeArr = []
        for el in e["hrsOfOperation"]:
            timeArr.append(el["daysShort"] + " : " + el["hours"])
        hours = ", ".join(timeArr)
        if hours.count("Closed") > 1:
            hours = missingString
            typ = "Closed"
        result.append(
            [
                locator_domain,
                missingString,
                name,
                street,
                city,
                state,
                zp,
                country,
                storenum,
                phone,
                typ,
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
