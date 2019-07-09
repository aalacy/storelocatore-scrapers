const Apify = require('apify');
const axios = require('axios');
const domain = "amf.com"

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: "GET",
    url: "https://www.amf.com/bowlero-location/finder?_format=json"
  }).then((resp) => {
    returnData = [];
    for (let entry of resp.data){
      returnData.push(mapData(entry));
    }
    return returnData;
  }).catch((e) => {
    handleError(e);
  })


}

function mapData(e){
  return {
    locator_domain: domain,
    location_name: e.name,
    street_address: e.address1,
    city: e.state == "" ? e.city.split(',')[0].trim() : e.city,
    state: e.state == "" ? fixProvince(e.city.split(',')[1].trim()) : e.state,
    zip: e.zip,
    country_code: e.state == "" ? "CA" : "US",
    store_number: e.centerNumber,
    phone: e.phone,
    location_type: e.brand,
    latitude: e.lat,
    longitude: e.lng,
    hours_of_operation: buildHours(e.hours)
  }
}

function buildHours(hours){
  try {
    retArr = []
    for (h of hours[0]['hours']){
      retArr.push(`${h.label} ${h.startTime} - ${h.endTime}`)
    }
    return retArr.join(', ');
  } catch (e){}
  return '<MISSING>';
}

function fixProvince(province){
  switch (province) {
    case 'Ont': province = 'Ontario'; break;
    default: break;
  }
  return province;
}

function handleError(e){
  console.error("Error retrieving data for Amegy Bank", e)
}
