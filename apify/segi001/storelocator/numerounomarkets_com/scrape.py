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
    locator_domain = "https://www.numerouno.market/"
    missingString = "<MISSING>"
    api = "https://www.numerouno.market/"

    def retrieveResults():
        s = bs4.BeautifulSoup(
            sgrequests.SgRequests()
            .get(
                api,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                },
            )
            .text,
            features="lxml",
        )
        res = []
        for el in s.findAll("div", {"class": "row sqs-row"})[-3]:
            for e in el.findAll("div", {"class": "sqs-block-content"}):
                arr = e.findAll("strong")
                if len(arr) == 0:
                    pass
                else:
                    name = arr[0].text.strip().replace(":", "")
                    phone = arr[1].text.strip()
                    street = arr[2].text.strip()
                    addr = arr[3].text.strip().split(",")
                    city = addr[0].strip()
                    state = addr[1].strip().split(" ")[0]
                    zp = addr[1].strip().split(" ")[1]
                    store_num = name.replace("Numero Uno", "").strip()
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
                            store_num,
                            phone,
                            missingString,
                            missingString,
                            missingString,
                            missingString,
                        ]
                    )
        return res

    result = retrieveResults()
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
