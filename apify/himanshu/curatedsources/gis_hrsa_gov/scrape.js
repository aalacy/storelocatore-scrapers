const request = require('request');
const Apify = require('apify');
var items = []
var cnt = 1
var output = []
var req = 1
async function layer_handler(layer, service_url) {
    return new Promise((resolve, reject) => {
        setInterval(() => {
            var fail = 0
            for (i = 0; i < 80; i++) {
                if (req < 80) {
                    req = req + 1;
                    request(service_url + "/" + layer["id"] + "/" + cnt + "?f=pjson", (err, res) => {
                        try {
                            var data = JSON.parse(res.body)
                                // console.log(data);
                                // console.log("1");
                            if (data.hasOwnProperty("error")) {
                                req = req - 1
                                fail = fail + 1
                                if (fail >= 5) {
                                    resolve()
                                    clearInterval(this);
                                }
                            } else {
                                var street_address = "";
                                var city = "";
                                var state = "";
                                var name = "";
                                var zip = "";
                                var phone = "";
                                var store_number = '';
                                // these are the geometries from the website
                                var x = data["feature"]["geometry"]["x"]
                                var y = data["feature"]["geometry"]["y"]
                                if (data["feature"]["attributes"].hasOwnProperty("CMS_PROVIDER_ADDRESS")) {
                                    name = data["feature"]["attributes"]["FACILITY_NM"]
                                    street_address = data["feature"]["attributes"]["CMS_PROVIDER_ADDRESS"]
                                    city = data["feature"]["attributes"]["CMS_PROVIDER_CITY"]
                                    state = data["feature"]["attributes"]["CMS_PROVIDER_STATE_ABBR"]
                                    zip = data["feature"]["attributes"]["CMS_PROVIDER_ZIP_CD"]
                                    phone = data["feature"]["attributes"]["PHONE_NUM"]
                                    store_number = data["feature"]["attributes"]["CMS_PROVIDER_NUM"]
                                } else if (data["feature"]["attributes"].hasOwnProperty("SITE_ADDRESS")) {
                                    name = data["feature"]["attributes"]["GRANTEE_NM"]
                                    street_address = data["feature"]["attributes"]["SITE_ADDRESS"]
                                    city = data["feature"]["attributes"]["SITE_CITY"]
                                    state = data["feature"]["attributes"]["SITE_STATE_ABBR"]
                                    zip = data["feature"]["attributes"]["SITE_ZIP_CD"]
                                    phone = data["feature"]["attributes"]["SITE_PHONE_NUM"]
                                    store_number = data["feature"]["attributes"]["BHCMISID"]
                                } else if (data["feature"]["attributes"].hasOwnProperty("GRANTEE_ADDRESS")) {
                                    name = data["feature"]["attributes"]["GRANTEE_NM"]
                                    street_address = data["feature"]["attributes"]["GRANTEE_ADDRESS"]
                                    city = data["feature"]["attributes"]["GRANTEE_CITY"]
                                    state = data["feature"]["attributes"]["GRANTEE_STATE_ABBR"]
                                    zip = data["feature"]["attributes"]["GRANTEE_ZIP_CD"]
                                    phone = data["feature"]["attributes"]["CONTACT_PHONE_NUM"]
                                    store_number = data["feature"]["attributes"]["UDS_NUM"]
                                } else if (data["feature"]["attributes"].hasOwnProperty("VHA_S_ADD1")) {
                                    name = data["feature"]["attributes"]["VHA_STA_NAME"]
                                    street_address = data["feature"]["attributes"]["VHA_S_ADD1"] + " " + data["feature"]["attributes"]["VHA_S_ADD2"] + " " + data["feature"]["attributes"]["VHA_S_ADD3"] + " " + data["feature"]["attributes"]["VHA_S_ADD4"]
                                    city = data["feature"]["attributes"]["VHA_S_CITY"]
                                    state = data["feature"]["attributes"]["VHA_S_STATE"]
                                    if (data["feature"]["attributes"]["VHA_S_ZIP4"] === "") {
                                        zip = data["feature"]["attributes"]["VHA_S_ZIP"]
                                    } else {
                                        zip = data["feature"]["attributes"]["VHA_S_ZIP"] + "-" + data["feature"]["attributes"]["VHA_S_ZIP4"]
                                    }
                                    phone = data["feature"]["attributes"]["VHA_STA_PHONE"]
                                    store_number = data["feature"]["attributes"]["VHA_UNIQUESTAT"]
                                }
                                street_address = street_address.replace(/null/g, "");
                                street_address = street_address.replace(/  /g, "").trim();
                                city = city.replace(/null/g, "").trim();
                                state = state.replace(/null/g, "").trim();
                                zip = zip.replace(/-null/g, "").trim();
                                if (!output.includes(name + " " + street_address)) {
                                    output.push(name + " " + street_address)
                                    items.push({
                                        locator_domain: "https://gis.hrsa.gov",
                                        location_name: name ? name : "<MISSING>",
                                        street_address: street_address ? street_address : "<MISSING>",
                                        city: city ? city : "<MISSING>",
                                        state: state ? state : "<MISSING>",
                                        zip: zip ? zip : "<MISSING>",
                                        country_code: "US",
                                        store_number: store_number ? store_number : "<MISSING>",
                                        phone: phone ? phone : "<MISSING>",
                                        location_type: layer["name"],
                                        latitude: "<MISSING>",
                                        longitude: "<MISSING>",
                                        hours_of_operation: "<MISSING>",
                                        page_url: service_url + "/" + layer["id"] + "/" + data["feature"]["attributes"]["OBJECTID"] + "?f=pjson"
                                    });
                                }
                                req = req - 1
                            }
                        } catch (exce) {
                            fail = fail + 1
                            req = req - 1
                        }
                    })
                    cnt = cnt + 1;
                }
            }
        }, 10000)
    })
}

function service_handler(service) {
    return new Promise((resolve, reject) => {
        var service_url = "https://gis.hrsa.gov/arcgis/rest/services/" + service["name"] + "/FeatureServer"
            // console.log(service_url)
        request(service_url + "?f=pjson", (err, res) => {
            var layers = JSON.parse(res.body)["layers"]

            function layerfun(i) {
                if (layers.length > i) {
                    layer_handler(layers[i], service_url).then(() => {
                        req = 1
                        cnt = 1
                        layerfun(i + 1)
                    })
                } else {
                    resolve()
                }
            }
            layerfun(0)
        })
    })
}

function scrape() {
    return new Promise((resolve, reject) => {
        request(`https://gis.hrsa.gov/arcgis/rest/services/HealthCareFacilities?f=pjson`, (err, res) => {
            var services = JSON.parse(res.body)["services"]

            function servicefun(i) {
                if (services.length > i) {
                    if (services[i].type == "FeatureServer") {
                        service_handler(services[i]).then(() => {
                            servicefun(i + 1)
                        })
                    } else {
                        servicefun(i + 1)
                    }
                } else {
                    resolve(items)
                }
            }
            servicefun(0)
        })
    });
}
Apify.main(async() => {
    const data = await scrape();
    await Apify.pushData(data);
});


// scrape();