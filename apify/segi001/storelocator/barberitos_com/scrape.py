import csv
import sgrequests
import json
import bs4


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
    locator_domain = "https://www.barberitos.com/"
    api = "https://www.barberitos.com/wp-admin/admin-ajax.php"
    missingString = "<MISSING>"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }

    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    sess = sgrequests.SgRequests()

    d = json.loads(sess.post(api, data=data, headers=header).text)

    result = []

    for s in d:
        name = d[s]["na"]
        store_num = d[s]["ID"]
        lat = d[s]["lat"]
        lng = d[s]["lng"]
        zp = d[s]["zp"]
        state = d[s]["rg"]
        street = d[s]["st"]
        phone = missingString
        city = d[s]["ct"]
        page_url = d[s]["gu"]
        hours = missingString

        if "post_type" in page_url:
            pass
        else:
            soup = bs4.BeautifulSoup(
                sess.get(page_url, headers=header).text, features="lxml"
            )
            hours = (
                soup.find("div", {"class": "store_locator_single_opening_hours"})
                .get_text(separator=", ")
                .replace("Hours, ", "")
            )

        if d[s]["te"] == "":
            phone = missingString
        else:
            phone = d[s]["te"]

        location_type = missingString

        if "Coming Soon" in name:
            location_type = "Coming Soon"

        result.append(
            [
                locator_domain,
                page_url,
                name,
                street,
                city,
                state,
                zp,
                missingString,
                store_num,
                phone,
                location_type,
                lat,
                lng,
                hours,
            ]
        )

    result = [missingString if x == " " else x for x in result]

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
