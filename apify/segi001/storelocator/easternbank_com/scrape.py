import csv
import sgrequests
import bs4


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
    stores = []

    locator_domain = "https://www.easternbank.com/"
    missingString = "<MISSING>"

    def res(result):
        return [ele for ind, ele in enumerate(result) if ele not in result[:ind]]

    def storeEndpoint(url, result):
        sess = sgrequests.SgRequests()
        request = sess.get(url).text
        soup = bs4.BeautifulSoup(request, features="lxml")
        for s in soup.findAll("div", {"class": "views-row"}):
            name = (
                s.find("div", {"class": "map-location-title"})
                .text.replace(
                    s.find("span", {"class": "map-location-title--counter"}).text, ""
                )
                .replace(s.find("span", {"class": "map-location-title--type"}).text, "")
            )
            street_address = ""
            address = s.find("span", {"class": "address-line1"})
            address_line2 = s.find("span", {"class": "address-line2"})
            if address_line2:
                street_address = "{} {}".format(address.text, address_line2.text)
            else:
                if address:
                    street_address = address.text
                else:
                    street_address = missingString
            city = s.find("span", {"class": "locality"}).text
            state = s.find("span", {"class": "administrative-area"}).text
            zipc = s.find("span", {"class": "postal-code"}).text
            phone = ""
            if s.find(
                "div", {"class": "views-field views-field-field-location-phone-number"}
            ):
                phone = s.find(
                    "div",
                    {"class": "views-field views-field-field-location-phone-number"},
                ).text
            else:
                phone = missingString
            location_type = s.find("span", {"class": "map-location-title--type"}).text
            lat = s.find("div", {"class": "location-coordinates"})["data-loc-lat"]
            lng = s.find("div", {"class": "location-coordinates"})["data-loc-lng"]
            hours = s.find("div", {"class": "office-hours"}).text.strip().split(r"\n")

            result.append(
                [
                    locator_domain,
                    missingString,
                    name,
                    street_address,
                    city,
                    state,
                    zipc,
                    missingString,
                    missingString,
                    phone,
                    location_type.replace("(", "").replace(")", ""),
                    lat,
                    lng,
                    hours[0].strip().replace(u"\n", " "),
                ]
            )

    storeEndpoint(
        "https://www.easternbank.com/locations?geolocation_geocoder_google_geocoding_api=Boston%2C+MA+02110&geolocation_geocoder_google_geocoding_api_state=0&field_location_hours_day=&field_location_hours_starthours=&field_location_hours_endhours=&proximity=50&proximity-lat=&proximity-lng=",
        stores,
    )
    storeEndpoint(
        "https://www.easternbank.com/locations?geolocation_geocoder_google_geocoding_api=Manchester%2C+NH%2C+USA&geolocation_geocoder_google_geocoding_api_state=1&field_location_hours_day=&field_location_hours_starthours=&field_location_hours_endhours=&proximity=50&proximity-lat=42.9956397&proximity-lng=-71.4547891",
        stores,
    )
    storeEndpoint(
        "https://www.easternbank.com/locations?geolocation_geocoder_google_geocoding_api=Leominster%2C+MA+01453&geolocation_geocoder_google_geocoding_api_state=0&field_location_hours_day=&field_location_hours_starthours=&field_location_hours_endhours=&proximity=50&proximity-lat=&proximity-lng=",
        stores,
    )

    result = res(stores)
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
