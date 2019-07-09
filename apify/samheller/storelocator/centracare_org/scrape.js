const Apify = require('apify');
const axios = require('axios');
const domain = 'centracare.org';
const url = 'https://centracare-scheduling.adventhealth.io/ccrest/api/smartappts/locsall';

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({method: "GET", url: url}).then((resp) => {
    returnData = [];
    for (let entry of resp.data.CC_getlocs){returnData.push(mapData(entry));}
    return returnData;
  }).catch((e) => {handleError(e);})
}

function mapData(e){
  return {
    locator_domain: domain,
    location_name: e.location_name,
    street_address: e.address_line_1 + e.address_line_2,
    city: e.city,
    state: e.state,
    zip: e.zip,
    country_code: "US",
    store_number: e.locid,
    phone: e.phone,
    location_type: '<MISSING>',
    latitude: e.lat,
    longitude: e.lng,
    hours_of_operation: buildHours(e)
  }
}

function buildHours(e){
  ret = "";
  ret = ret + `Sunday ${e.open_sun} - ${e.close_sun}`
  ret = ret + `Monday ${e.open_mon} - ${e.close_mon}`
  ret = ret + `Tuesday ${e.open_tue} - ${e.close_tue}`
  ret = ret + `Wednesday ${e.open_wed} - ${e.close_wed}`
  ret = ret + `Thursday ${e.open_thu} - ${e.close_thu}`
  ret = ret + `Friday ${e.open_fri} - ${e.close_fri}`
  ret = ret + `Saturday ${e.open_sat} - ${e.close_sat}`
  return ret;
}


function handleError(e){
  console.error("Error retrieving centracare.org locations: ", e);
}
/*
 {
      "locid": 1,
      "location_id": "C8AE7FC1-320E-475E-ADF9-03EEA445285A",
      "location_name_display": "AdventHealth Centra Care Altamonte",
      "location_name": "AdventHealth Centra Care Altamonte",
      "address_line_1": "440 W Hwy 436",
      "address_line_2": " ",
      "city": "Altamonte Springs",
      "state": "FL",
      "zip": "32714",
      "phone": "4077882000",
      "fax": "4077882024",
      "center": "3410",
      "lat": 28.661294937134,
      "lng": -81.39875793457,
      "open_sun": "0800",
      "open_mon": "0800",
      "open_tue": "0800",
      "open_wed": "0800",
      "open_thu": "0800",
      "open_fri": "0800",
      "open_sat": "0800",
      "close_sun": "1700",
      "close_mon": "2000",
      "close_tue": "2000",
      "close_wed": "2000",
      "close_thu": "2000",
      "close_fri": "2000",
      "close_sat": "1700",
      "Active": 1,
      "org_id": 1,
      "loctype": "cc",
      "work_start": "2019-07-09 08:00:00",
      "work_end": "2019-07-09 20:00:00",
      "is_holiday": 0
    },
    */