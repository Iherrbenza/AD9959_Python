
/* Control a AD9959 DDS with a ESP32 microcontroller 
 *  
 * The system is uses a 32 pin
 * ESP32-DevKitC Core Board ESP32
 * https://www.espressif.com/en/products/devkits/esp32-devkitc/overview
 * 
 * // Hardware pin connections 

//  ESP32             -> AD9959    
//  Pin GND GND       -> GND     
//  Pin 14  SCLK      -> SCLK      
//  Pin 12  MISO      -> SDIO2     
//  Pin 13  MOSI      -> SDIO0    
//  Pin 15  CS        -> CSB       
//  Pin 27  UPD       -> IO Update 
//  Pin 26  RST       -> resetPin  
//  Pin 32  SYNC      -> SDIO3     
//  Pin 19  Interrupt -> none (external trigger)
 * 
 *  
 * created 16/07/2021 by Ivan Herrera Benzaquen
 * at SWinburne University of Technology
 */

 
#include <SPI.h>
#include <WiFi.h>
#include "Webserver.h"

String currentline = "";                     // temporal String to retain incoming data from the client

// list iteraction variables
# define listdim 10000                       // max number of elements in the memory list.
# define INT 19                              // pin to listen for the IO_updates, interrupt pin.
volatile int list_ele = 0;                   // iteration variable to go through the list.
static uint32_t cycletime = 0;               // variable to count time.
volatile unsigned long maxcycletime = 120000;// max time the system will be in list mode, can be changed.
volatile int n_items = 0;                    // number of items to iterate trough.
unsigned long long spi_memory[listdim];      // setin the memory list, (64bits per item max).

//SPI parameters
//pins definitions
#define SCLK 14                              // SPI Clock
#define MISO 12                              // SPI data IN
#define MOSI 13                              // SPI data out
#define CS   15                              // chip select
#define UPD  27                              // update pin of the AD9959
#define RST  26                              // reset pin of the AD9959
#define SYNC 32                              // communication reset pin of the AD9959
#define spiClk  20000000                     // SPI clock 20 MHz
SPIClass * hspi = NULL;                      // uninitalised pointers to SPI objects

// Register address definitions for hard initialisation
#define CSR  0x00                            // Channel Select Register
#define FR1  0x01                            // Function Register 1
#define FR2  0x02                            // Function Register 2
#define CFR  0x03                            // Channel Function Register
#define CFTW 0x04                            // Channel Frequency Word
#define ACR  0x06                            // Amplitude Control Register
#define MultiplierEnable 0x1000              // 0 means bypass the amplitude multiplier

// declaring functions.
void init_DDS(void);
void reset_DDS(void);
void reset_comm(void);
void IO_update(void);
void direct_spi(String);
void memory_spi(unsigned long long);
void memory_storage(String);

// interrupt function
void IRAM_ATTR isr() {
//  each time pulse arrives to PIN INT will execute
  list_ele += 1;
  memory_spi(spi_memory[list_ele]);
  }

void setup() {

  // initalised serial communication
  Serial.begin(115200);

  // Connect to Wi-Fi network with SSID and password
  connect_wifi();
  
  // init digital pin outputs in the ESP32
  pinMode(CS, OUTPUT);          // HSPI CS chip select
  pinMode(UPD, OUTPUT);         // Update AD9959 
  pinMode(RST, OUTPUT);         // Reset AD9959 
  pinMode(SYNC, OUTPUT);        // Reset SPI buffers on the AD9959
  pinMode(INT, INPUT_PULLUP);   // Interrupt pin for list mode
 
  //initialise the SPIClass attached to HSPI 
  hspi = new SPIClass(HSPI);
  //initialise hspi with default pins
  hspi->begin(SCLK,MISO,MOSI,CS); 
  //init SPI communication
  hspi->beginTransaction(SPISettings(spiClk, MSBFIRST, SPI_MODE3));
  
  // DDS reset and initialisation
  init_DDS();  // init the DDS with the target setup values
  delay(10);
  //digitalWrite(CS, LOW);
  }

// the loop function runs over and over again until power down or reset---------------------
void loop() {
   
   WiFiClient client = server.available();   // Listen for incoming clients

   if (client) {                             // If a new client connects,
     
    while (client.connected()) {             // loop while the client's connected
      
      if (client.available()) {              // if there's bytes to read from the client,
        
        // check first character, this will decide what info is coming
        char ch = client.read();

        // initilisiation DDS---------------------------------------------------------------
        if(ch == 'i'){
          init_DDS();
          Serial.println("DDS initialised");
          }

        // okay message---------------------------------------------------------------------
        if(ch == '?'){
          client.write('O');
          Serial.println("DDS");
          }

        // sofware reset DDS----------------------------------------------------------------
        if(ch == 'r'){
          reset_DDS();
          Serial.println("DDS reset");
          }

        // sofware reset communication DDS--------------------------------------------------
        if(ch == 's'){
          reset_comm();
          Serial.println("DDS communications reset");
          }

        // sofware update communication DDS--------------------------------------------------
        if(ch == 'u'){
          IO_update();
          Serial.println("update registers");
          }
        
        // direct writing of SPI-------------------------------------------------------------
        if(ch == 'd'){
          while((ch = client.read()) != '\n'){
            currentline += ch; // read line
            }
          if (currentline.length() > 0 ){ 
            direct_spi(currentline);                    // parse the string and transfer via SPI       
            currentline = ""; 
            }
          }
                    
         // set number of commands in the list memory-------------------------------------
         if(ch == 'n'){
           while((ch = client.read()) != '\n'){
             currentline += ch; // read line
             }
          n_items = currentline.toInt();
          currentline = ""; 
          }
         
         // set max cycle time------------------------------------------------------------
         if(ch == 't'){
           while((ch = client.read()) != '\n'){
             currentline += ch; // read line
             }
          maxcycletime = currentline.toInt();
          currentline = ""; 
          }
          
        // storage command in the list memory -------------------------------------------------  
        if(ch == 'm'){
          while((ch = client.read()) != '\n'){
            currentline += ch; // read line
            }
          if (currentline.length() > 0 ){  
            memory_storage(currentline);                  // storage into the memory list
            currentline = ""; 
            }
          }
        
        // clean the list memory -------------------------------------------------------------  
        if(ch == 'k'){
          for(int i = 0; i<listdim; i++){spi_memory[i] = 0;}
          n_items = 0;
          }
          
        // go to list mode -------------------------------------------------------------------    
        if(ch == 'l'){
          list_ele = 0;                                     // set list element counter to zero
          pinMode(UPD, INPUT_PULLUP);                       // set UPD PIN as an input with pullup resistor (the INT PIN will control the update of the registers )
          digitalWrite(CS, LOW);                            
          memory_spi(spi_memory[list_ele]);                 // write into the registers the 1st element of the list(It won't be updated till a pulse arrives to INT PIN
          attachInterrupt(INT, isr, FALLING);               // enable interrupts, each pulse (falling edge) will trigger the isr function
          cycletime = millis();                             // start the time counter 
          while(1){
            if (list_ele + 1 > n_items){                    // if list counter is larger than the number of elements in the list go out from the list mode
              detachInterrupt(INT);                         // and detach interrups
              break;  
              }
            if (millis()- cycletime > maxcycletime){        // if time counter is larger than max cycletime go out from the list mode
              detachInterrupt(INT);                         // and detach interrupts
              break;  
              } 
            }
            digitalWrite(CS, HIGH);
            pinMode(UPD, OUTPUT);                           // set the UPD PIN as output, ESP32 will controll the registers updates
            list_ele = 0;                                   // reset list elements counter
          } 
        
        }
      }
    }
        
    //check if there was any problem with the network and reconnect
    if (WiFi.status() != WL_CONNECTED){
      Serial.println("disconnected");
      connect_wifi();
      }
    
  }
// end of the loop function------------------------------------------------------------------------------


// functions --------------------------------------------------------------------------------------------
void reset_DDS(){ 
  // pulse the reset pin to reset the board
  digitalWrite(RST, HIGH); //pulse the update pin
  delay(10);
  digitalWrite(RST, LOW);
  }

void reset_comm(){
  // resets the DDS com buffers incase of incorrect communication
  digitalWrite(SYNC, HIGH);
  digitalWrite(SYNC, LOW);

  }
void IO_update(){
  // pulse to update the registers
  digitalWrite(UPD, HIGH); 
  digitalWrite(UPD, LOW);
  }

void init_DDS() {
  // hard code of the initialisation of the DDS
  // the will reset with all the amp values to zero and something more
  digitalWrite(CS, HIGH);
  digitalWrite(UPD, LOW); 
  digitalWrite(RST, LOW); 
  digitalWrite(SYNC, LOW);  
  delay(1);
  reset_DDS();                            // reset DDS to default values
  delay(1);
  reset_comm();                           // if any SPI communications went wrong
  delay(1);
  digitalWrite(CS, LOW);
  hspi->transfer(FR1);                    // write the values into the FR1 register 3 bytes wide 
  hspi->transfer(0b11010011);             //PPL divider x20, VCO activated, pump charge maximum(to test can be noisy)
  hspi->transfer(0b00000000);
  hspi->transfer(0b00000000);
  delayMicroseconds(500);
  hspi->transfer(FR2);                    // write the values into the FR2 register 2 bytes wide   
  hspi->transfer(0b00000000);
  hspi->transfer(0b00000000);
  delayMicroseconds(500);
  hspi->transfer(CFR);                    // write the values into the CFR register 3 bytes wide 
  hspi->transfer(0b00000000);             // Modulation off
  hspi->transfer(0b00000011);             // Full scale DAC
  hspi->transfer(0b00010100);
  IO_update();
  digitalWrite(CS, HIGH);
  }

void direct_spi(String input){
  // transfer and parsed the string received from the WiFi to the SPi channel
  unsigned int l = input.length();
  unsigned long long spi_mem = strtoll(input.c_str(),NULL,0);
  int spi_out;
  digitalWrite(CS, LOW);
  if (l % 2 == 0){ l = 4*(l-2)-8;}
  else{ l = 4*(l-1)-8;}
  for (int i = l; i > -1; i = i - 8){
    spi_out = (spi_mem >> i) & 0xFF;
    if( i == l and spi_out > 0x18){spi_out = 0x00;}
    hspi->transfer(spi_out);
    }
    IO_update();
    digitalWrite(CS, HIGH);    
  }
  
void memory_spi(unsigned long long input){
  // transfer from memory to the SPI channel
  int spi_out = 0;
  bool flag = 1;
  digitalWrite(CS, LOW);
  for (int i = 56; i > -8; i = i - 8){
    spi_out = (input >> i) & 0xFF;
    if( flag and spi_out > 0x00 ){
      if(spi_out < 0x19){hspi->transfer(spi_out); flag = 0;}
      else if(spi_out == 0x20){spi_out = 0x00; hspi->transfer(spi_out);flag = 0;}
      }
    else if(!flag ){
      hspi->transfer(spi_out);
      }
    }
  }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      

 void memory_storage(String input){
  // save in memory the string received from the WiFi to the SPi channel

  unsigned int l = input.length();
  int j = 0;   
  String c = ""; 
    for(int i = 0; i<=l; i++){
      if (     input[i] == 'n'){j             = c.toInt();                 c = "";}
      else if (input[i] == 'w'){spi_memory[j] = strtoll(c.c_str(),NULL,0); c = "";}
      else {c += input[i];}}
   }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
