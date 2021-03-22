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
    locator_domain = "http://navistarsupplier.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(
            l,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
            },
        )

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    s = initSoup("http://navistarsupplier.com/Locations/PartsLocations.aspx")

    result = []

    for table in s.findAll("table", {"class": "EU_DataTable"}):
        if "United States" in table.find("th").text:
            for tr in table.findAll("tr"):
                if "United States" in tr.text:
                    pass
                else:
                    name = tr.find("a").text.strip()
                    street = tr.find("span").get_text("\n").strip().split("\n")[0]
                    city = (
                        tr.find("span")
                        .get_text("\n")
                        .strip()
                        .split("\n")[-1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                    state = (
                        tr.find("span")
                        .get_text("\n")
                        .strip()
                        .split("\n")[-1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split(" ")[0]
                        .strip()
                    )
                    zp = list(
                        filter(
                            None,
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[1]
                            .strip()
                            .split(" "),
                        )
                    )[1].strip()
                    result.append(
                        [
                            locator_domain.strip(),
                            missingString.strip(),
                            name.strip(),
                            street.strip(),
                            city.strip(),
                            state.strip(),
                            zp.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                        ]
                    )
        else:
            for tr in table.findAll("tr"):
                if "Canada" in tr.text:
                    name = tr.find("a").text.strip()
                    street = tr.find("span").get_text("\n").strip().split("\n")[0]
                    if (
                        len(
                            list(
                                filter(
                                    None,
                                    tr.find("span")
                                    .get_text("\n")
                                    .strip()
                                    .split("\n")[-1]
                                    .strip()
                                    .split(",")[1]
                                    .strip()
                                    .split(" "),
                                )
                            )
                        )
                        == 1
                    ):
                        city = (
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[0]
                            .strip()
                            + ", "
                            + tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[1]
                            .strip()
                        )
                        state = (
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[2]
                            .strip()
                            .split(" ")[0]
                        )
                        zp = (
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[2]
                            .strip()
                            .split(" ")[1]
                            + " "
                            + tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[2]
                            .strip()
                            .split(" ")[2]
                        )
                    else:
                        city = (
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[0]
                            .strip()
                        )
                        state = (
                            tr.find("span")
                            .get_text("\n")
                            .strip()
                            .split("\n")[-1]
                            .strip()
                            .split(",")[1]
                            .strip()
                            .split(" ")[0]
                            .strip()
                        )
                        zp = (
                            list(
                                filter(
                                    None,
                                    tr.find("span")
                                    .get_text("\n")
                                    .strip()
                                    .split("\n")[-1]
                                    .strip()
                                    .split(",")[1]
                                    .strip()
                                    .split(" "),
                                )
                            )[1]
                            + " "
                            + list(
                                filter(
                                    None,
                                    tr.find("span")
                                    .get_text("\n")
                                    .strip()
                                    .split("\n")[-1]
                                    .strip()
                                    .split(",")[1]
                                    .strip()
                                    .split(" "),
                                )
                            )[2]
                        )
                    result.append(
                        [
                            locator_domain.strip(),
                            missingString.strip(),
                            name.strip(),
                            street.strip(),
                            city.strip(),
                            state.strip(),
                            zp.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                            missingString.strip(),
                        ]
                    )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
