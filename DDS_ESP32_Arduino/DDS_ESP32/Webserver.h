/* WiFi functionalities 
 *  
 * Put here you ssd/password to connect the board to your local network 
 * 
 * created 16/07/2021 by Ivan Herrera Benzaquen
 * at SWinburne University of Technology
 */

// WiFi variables
const char* ssid = "";
const char* password = "";


// Set web server port number to 80
WiFiServer server(80);

void connect_wifi(){ 
  // Connect to Wi-Fi network with SSID and password
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {  
    Serial.print("Trying to connect to ");
    Serial.println(ssid);
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println(WiFi.macAddress());
  server.begin();

  }
