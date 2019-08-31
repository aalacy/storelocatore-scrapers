const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://tumbles.net/';
async function scrape(){

    return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
 
        const $  =cheerio.load(html);
        var items=[];

var main = $('.dropdown').find('.dropdown-menu').find('li')//.find('a').attr('href');
function mainhead(i)

{
  if(main.length>i)

    {

                const link = $(main[i]).find('a').attr('href');
              //  console.log(link);

                request(link,(err,res,html)=>{    
                    if(!err && res.statusCode==200){
                      const $ =cheerio.load(html);
        
                      var main1 = $('address');

                      var location_name = main1.find('p').find('strong').text().trim();

                      var tmp_address = main1.find('p').eq(1).text();

                      var tmp_address1 = tmp_address.split(',');

                      var phone = main1.find('p').eq(2).text();

                      var hour = $('.hours').find('ul').find('li').text();
 


                      if(tmp_address1.length == 4){
                        var address = tmp_address1[0].trim();
                        var city = tmp_address1[1].trim();
                        var state = tmp_address1[2].trim();
                        var zip = tmp_address1[3].trim();
  

                      }

                      else if(tmp_address1.length == 5){
                        var address = tmp_address1[0] + tmp_address1[1].trim();
                        var city = tmp_address1[2].trim();
                        var state = tmp_address1[3].trim();
                        var zip = tmp_address1[4].trim();
  
                      }
                   
                      items.push({ 

                        locator_domain: url, 
                        location_name:location_name,
                        street_address: address,
                        city: city,
                        state: state,
                        zip: zip,
                        country_code: 'US',
                        store_number: '<MISSING>',
                        phone: phone, 
                        location_type: 'tumbles',
                        latitude:'<MISSING>',
                        longitude : '<MISSING>',
                        hours_of_operation:hour
         
                     
                      });
    
                      mainhead(i+1);

                   
                    }
                    
                });
        

            }
     

        else{
       
          resolve(items);
      
         }
      } 
      
      mainhead(0);

 }
});

});

}

Apify.main(async () => {

    

    const data = await scrape();
    
  
    await Apify.pushData(data);
  
  });
