const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'http://meadowsfrozencustard.com/columns/';

 
 
async function scrape(){
  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{
                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                           
                          var items=[];

                           var main = $('.page-content').find('.col-lg-3');
                           function mainhead(i)

                             {
                                 if(main.length>i)
   
                                     {
                             
                            var location_name = $('.page-content').find('.col-lg-3').eq(i).children('h3').text().trim();
                           
                             
                           
                             var address_tmp = $('.page-content').find('.col-lg-3').eq(i).children('p').text().trim().split(',');
                            
                             if(address_tmp.length == 1){
                               var address_tmp1 = address_tmp[0].split(' ');
                               var address = address_tmp1[0]+'' +address_tmp1[1]+'' +address_tmp1[2]+'' +address_tmp1[3];
                               var city = address_tmp1[4];
                               var state = address_tmp1[5];
                               var zip = address_tmp1[6];
                               
                           

                             }
                             else if(address_tmp.length == 2){
                              var address = address_tmp[0].replace('New Alexandria','<MISSING>').replace('Williamsburg','1222 Richmond RD');
                              var city = address_tmp[0];
                              var state_tmp = address_tmp[1].split(' ');
                              var state = state_tmp[1];
                              var zip = '<MISSING>';
                              

                            }
                            else if(address_tmp.length == 3){
                              var address = address_tmp[0];
                              var city = address_tmp[1];
                              var state_tmp = address_tmp[2].split(' ');
                               if(state_tmp.length == 3){
                                 var state = state_tmp[1];
                                
                                 var zip = state_tmp[2];

                               }
                               else if(state_tmp.length == 4){
                                 var state = state_tmp[1]+' '+state_tmp[2];
                                 
                                 var zip = state_tmp[3];
                              }
                              else if(state_tmp.length == 5){
                                var state =  '<MISSING>';
                                var zip = '<MISSING>';

                                 
                              }
                              
                              
                               
                            }
                            else if(address_tmp.length == 4){

                              var address = address_tmp[1];
                              
                              var city = address_tmp[2];
                              var state_tmp = address_tmp[3].split(' ');
                              var state = state_tmp[1];
                              var zip = state_tmp[2];

                          
                               
                            }
                             
                            if((location_name!='')){
                              
                              items.push({  

                                          locator_domain: 'http://meadowsfrozencustard.com/', 
          
                                          location_name: location_name, 
                              
                                          street_address: address,
                              
                                          city: city, 
                              
                                          state: state,
                              
                                          zip:  zip,
                              
                                          country_code: 'US',
                              
                                          store_number: '<MISSING>',
                              
                                          phone:  '<INACCESSIBLE>',
                              
                                          location_type: 'meadowsfrozencustard',
                              
                                          latitude: '<MISSING>',
                              
                                          longitude: '<MISSING>', 
                              
                                          hours_of_operation: ' <INACCESSIBLE>'});
                              }
                                          mainhead(i+1);
                                    
                               
                         
                         
                        }
                                
                                
                          else{
                      
                          resolve(items);
                      
                          }
                    } 
  
                    mainhead(0);  
                              }
 });
})
}
  
Apify.main(async () => {

    

    const data = await scrape();
    
  await Apify.pushData(data);
    
  
  });
