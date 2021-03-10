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
    locator_domain = "https://www.westelm.co.uk/"
    missingString = "<MISSING>"

    sess = sgrequests.SgRequests()

    req = sess.get("https://www.westelm.co.uk/store-locations").text

    soup = bs4.BeautifulSoup(req, features="lxml")

    locationRows = soup.findAll("div", {"class": "row storeLocationsRow"})

    slugs = []

    for locationRow in locationRows:
        a = locationRow.findAll("a")
        for ass in a:
            if ass["href"] == "#":
                pass
            else:
                slugs.append(ass["href"].split())

    result = []

    for s in slugs:
        url = "{}{}".format(locator_domain, s[0].replace("/", ""))
        r = sess.get(url).text
        st = bs4.BeautifulSoup(r, features="lxml")
        td = st.find("td", {"class": "bondi-junction-table-big-padding-cell"})
        phone = td.find("a").text
        ad = (
            td.get_text(separator="$")
            .replace("Phone:", "")
            .replace(phone, "")
            .split("$")
        )
        ad = list(filter(None, ad))
        name = ad[0]
        street = missingString
        if " Unit SU1233 " in ad:
            street = "{} {}".format(ad[1].strip(), ad[2].strip())
        else:
            street = ad[1].strip()
        state = ad[-2].split(",")[1].strip()
        zp = ad[-2].replace("London", "").split(",")[0].strip()
        tr = st.findAll("tr")
        city = missingString
        if "London" in ad[-2]:
            city = "London"
        else:
            city = missingString
        if street == "Kingston upon Thames":
            city = street
            street = missingString
        hours = "{}, {}, {}, {}, {}, {}, {}".format(
            tr[3].text,
            tr[4].text,
            tr[5].text,
            tr[6].text,
            tr[7].text,
            tr[8].text,
            tr[9].text,
        ).replace(u"\xa0", u" ")
        result.append(
            [
                locator_domain,
                url,
                name,
                street,
                city,
                state,
                zp,
                state,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
