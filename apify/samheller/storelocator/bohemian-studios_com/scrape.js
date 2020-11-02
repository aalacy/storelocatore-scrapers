const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

Apify.main(async () => {
  const links = await pageList();
  for (l of links){
    loc = await scrape(l.url);
    await Apify.pushData([loc]);
  }
});

async function scrape(link){
  return await axios({
    method: "GET",
    url: link
  }).then((resp) => {
    dom = new JSDOM(resp.data)
    location = dom.window.document.querySelector('.sqs-block-content > h1').textContent;
    addr = dom.window.document.querySelector('.sqs-block-content > h3')
      .innerHTML  // Using HTML instead of text
      .replace("<br>", "\n")  // using linebreaks for address differentiation
      .replace(/\<.*\>/g, '') // remove extra markup
      .replace(/&.*;/g, '') //remove encoded entities
      .replace(',', '') //remove commas for city/state/zip parsing
      .split("\n");
    
    // Get street address
    street = addr[0];
    
    // Extract city/state/zip
    area = addr[1].split(" ").filter((e) => {return e.trim() != ""});
    zip = area.pop();
    state = area.pop();
    city = area.join(" ");

    return {
      locator_domain: 'bohemian-studios.com',
      location_name: location,
      street_address: street,
      city: city,
      state: state,
      zip: zip,
      country_code: "US",
      store_number: "<MISSING>",
      phone: "<MISSING>",
      location_type: "Studio",
      latitude: "<MISSING>",
      longitude: "<MISSING>",
      hours_of_operation: "<MISSING>",
    }

  })  
}

async function pageList(){
  return await axios({
    method: "GET",
    url: "https://bohemian-studios.com/"
  }).then((resp) => {
    dom = new JSDOM(resp.data);
    links = [];
    for (let l of dom.window.document.querySelector('.subnav').querySelectorAll('a')){
      links.push({url: "https://bohemian-studios.com" + l.getAttribute('href')})
    }
    return links;
  })
}

