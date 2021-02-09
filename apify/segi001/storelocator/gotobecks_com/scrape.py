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
    locator_domain = "https://gotobecks.com/"
    missingString = "<MISSING>"

    def allLocations():
        txt = (
            sgrequests.SgRequests()
            .get("https://gotobecks.com/index.php/locations/")
            .text
        )
        b = bs4.BeautifulSoup(txt, features="lxml")
        div = b.find("div", {"class": "entry-content"})
        p = div.findAll("p")
        res = []
        for ps in p:
            el = list(
                filter(
                    None,
                    ps.get_text(separator="\n")
                    .strip()
                    .replace(u"\xa0", "")
                    .split("\n"),
                )
            )
            if len(el) < 1:
                pass
            else:
                name = el[0].strip()
                street = el[1].strip()
                city = el[2].strip().split(",")[0].strip()
                state = el[2].strip().split(",")[1].strip().split(" ")[0].strip()
                zp = el[2].strip().split(",")[1].strip().split(" ")[1].strip()
                phone = el[-1]
                code = name.split(" ")[1].replace("(", "").replace(")", "").strip()
                res.append(
                    [
                        locator_domain,
                        missingString,
                        name,
                        street,
                        city,
                        state,
                        zp,
                        missingString,
                        code,
                        phone,
                        missingString,
                        missingString,
                        missingString,
                        missingString,
                    ]
                )
        return list(filter(None, res))

    result = allLocations()
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
