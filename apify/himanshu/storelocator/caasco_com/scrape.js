const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var tmp_url = 'https://www.caasco.com'
var url= "https://www.caasco.com/About-Us/Contact-Us/Store-Locations.aspx"

 
 
async function scrape(){
return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{
                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                           
                          var items=[];

                           var main = $('.interiortable').find('a');
                           function mainhead(i)

                           {
                               if(main.length>i)
 
                                   {
                             var link = tmp_url+ $('.interiortable').find('a').eq(i).attr('href');
                             
                             request(link,(err,res,html)=>{
                              if(!err && res.statusCode==200){
                                
                                    const $  =cheerio.load(html);
                                    main1 = $('.twocolmid-table').find('p').html();
                                    hour_tmp = $('.twocolmid-table').find('td:nth-child(2)').children('p');
                                    if(hour_tmp.length == 1){
                                      hour = $('.twocolmid-table').find('td:nth-child(2)').children('p').text().replace(/^\s+|\s+$/g, '').replace(/\n/g, '');
                                    }
                                    else if(hour_tmp.length == 2){
                                      hour = $('.twocolmid-table').find('tr:nth-child(1)').find('td:nth-child(2)').children('p').text().replace(/^\s+|\s+$/g, '').replace(/\n/g, '');
                                      
                                    }
                                   
                                    
                                    
                                    address_tmp = main1.split('<br>');
                                    var location_name = address_tmp[0].replace('CAA ','');
                                    var address = address_tmp[1].replace('Shops at Don Mills','20 Marie Labatte Road').replace(/^\s+|\s+$/g, '');

                                  
                                    
                                    if(address_tmp.length == 7 || 6){
                                      
                                      var city_tmp = address_tmp[2].trim().split(',');
                                         if(city_tmp.length == 3){
                                          var city = city_tmp[0].trim();
                                          var state =city_tmp[1].trim();
                                          var zip = city_tmp[2].trim();
                                          var phone =  address_tmp[3].trim().replace('Phone: ','').replace(/^\s+|\s+$/g, '');
                                         

                                         }
                                         else if(city_tmp.length == 1){
                                          var city_tmp = address_tmp[3].trim().split(',');
                                          var city = city_tmp[0].trim();
                                          var state =city_tmp[1].trim();
                                          var zip = city_tmp[2].trim();
                                          var phone =  address_tmp[4].trim().replace('Phone: ','').replace(/^\s+|\s+$/g, '');
                                          

                                         }
                                       
                                        
                                      
                                    }
                                    else if(address_tmp.length == 8){
                                      var city_tmp = address_tmp[3].trim().split(',');
                                      var city = city_tmp[0].trim();
                                      var state = city_tmp[1].trim();
                                      var zip = city_tmp[2].trim();
                                      var phone =address_tmp[4].trim().replace('Phone: ','').replace(/^\s+|\s+$/g, '');
                                     
                                      
                                    }
                                   
                                    
                                    items.push({  

                                      locator_domain: 'https://www.caasco.com', 
      
                                      location_name: location_name, 
                          
                                      street_address: address,
                          
                                      city: city, 
                          
                                      state: state,
                          
                                      zip:  zip,
                          
                                      country_code: 'US',
                          
                                      store_number: '<MISSING>',
                          
                                      phone: phone,
                          
                                      location_type: 'caasco',
                          
                                      latitude: '<MISSING>',
                          
                                      longitude:'<MISSING>', 
                          
                                      hours_of_operation: hour });
                                      mainhead(i+1);
                              }
                            });
                          }
                                          
                                          
                          else{
                      
                          resolve(items);
                      
                          }
                    } 
  
                    mainhead(1); 
                           
  }
 
 });
})
}
  
Apify.main(async () => {

    

    const data = await scrape();
   
    await Apify.pushData(data);
    
  
  });
