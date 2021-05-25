import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "texaco.co.uk"
    start_url = "https://locations.valero.com/en-us/Home/SearchForLocations"
    frms = [
        {
            "NEBound_Lat": "56.460148566650496",
            "NEBound_Long": "-0.8690270507812325",
            "SWBound_Lat": "52.64049136881006",
            "SWBound_Long": "-10.465584667968733",
            "center_Lat": "54.550319967730275",
            "center_Long": "-5.6673058593749825",
        },
        {
            "NEBound_Lat": "56.16766306111765",
            "NEBound_Long": "4.3494788085937675",
            "SWBound_Lat": "52.3193199730368",
            "SWBound_Long": "-5.2470788085937325",
            "center_Lat": "54.243491517077224",
            "center_Long": "-0.44879999999998255",
        },
        {
            "NEBound_Lat": "54.15351887803711",
            "NEBound_Long": "3.7562170898437675",
            "SWBound_Lat": "50.11081516745987",
            "SWBound_Long": "-5.8403405273437325",
            "center_Lat": "52.13216702274849",
            "center_Long": "-1.0420617187499825",
        },
    ]
    for formdata in frms:
        response = session.post(start_url, data=formdata)
        data = json.loads(response.text)

        for poi in data:
            store_url = (
                "https://locations.valero.com/en-us/LocationDetails/Index/{}/{}".format(
                    poi["DetailPageUrlID"], poi["LocationID"]
                )
            )
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += ", " + poi["AddressLine2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            if zip_code == "0":
                zip_code = "<MISSING>"
            country_code = poi["State"]
            if country_code != "GB":
                continue
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["LocationID"]
            store_number = store_number if store_number else "<MISSING>"
            location_type = ", ".join(poi["LocationDetailCodes"])
            location_type = location_type if location_type else "<MISSING>"
            phone = poi["Phone"]
            phone = phone if phone else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = str(latitude) if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = str(longitude) if longitude else "<MISSING>"
            hours_of_operation = poi["Hours"]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            item = [
                DOMAIN,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
