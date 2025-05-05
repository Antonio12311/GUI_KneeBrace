#include <mcp_can.h>
#include <SPI.h>

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
 #define SERIAL SerialUSB
#else
 #define SERIAL Serial
#endif

#define LED2 8
#define LED3 7
#define LED4 4
#define STOP_BTN 9
#define LED5 3

#define P_MIN -12.5f 
#define P_MAX 12.5f 
#define V_MIN -50.0f 
#define V_MAX  50.0f 
#define KP_MIN 0.0f 
#define KP_MAX 500.0f 
#define KD_MIN 0.0f 
#define KD_MAX 5.0f 
#define T_MIN -65.0f 
#define T_MAX 65.0f 

float p_in = 0.0f;
float v_in = 0.0f;
float kp_in = 0.0f;
float kd_in = 0.0f;
float t_in = 0.0f;

float p_out = 0.0f;
float v_out = 0.0f;
float t_out = 0.0f;

String id_s;
String p_out_s;
String t_out_s;
String volts;
String kp_in_s;
String coma = ",";
String total;
String py;
String mode = "\0";
String text1 = "Mode";
String text2 = " ";
String v_out_s;




const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

void setup() {
    SERIAL.begin(115200);
    while (!SERIAL);  // Espera a que la consola esté lista
    
    delay(1000);
    
    while (CAN_OK != CAN.begin(CAN_1000KBPS)) {
        SERIAL.println("CAN BUS Shield init fail");
        delay(100);
    }
    SERIAL.println("CAN BUS Shield init ok!");

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(STOP_BTN, INPUT);
    pinMode(LED5, OUTPUT);

    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    
    ExitMotorMode();
    Zero();
}

void loop() {
    if (Serial.available() > 0) {
        String py = Serial.readStringUntil('\n');  // Lee hasta encontrar '\n'
        py.trim();  // Elimina espacios en blanco y caracteres extra

        Serial.print("Recibido: ");
        Serial.println(py);  // Muestra el dato recibido

        float pyfl = py.toFloat();

        if (pyfl == 999.0) {
            kp_in = 0;
            kd_in = 0;
            t_in = 0;
            mode = "\0";
            py = "\0";
            ExitMotorMode();
            digitalWrite(LED2, LOW);
            digitalWrite(LED5, LOW);
            delay(10);

        } 
        else if (pyfl == 998.0) {
            // Zero();
            delay(10);
            digitalWrite(LED2, HIGH);
            digitalWrite(LED5, HIGH);
            EnterMotorMode();
            delay(10);
        } 
        else if (pyfl == 997.0) {
            Zero();
            delay(10);
        } 
        else {
          t_in = - pyfl;
          kp_in = 0;
          kd_in = 0;
        }
    }

    // Enviar datos por CAN Bus
    pack_cmd();

    // Recibir datos del CAN Bus
    if (CAN_MSGAVAIL == CAN.checkReceive()) {
        unpack_reply();
    }

    // Mostrar valores en el monitor serie
    p_out_s = String(p_out, 2);
    t_out_s = String(t_out, 2);
    total = p_out_s + coma + t_out_s;
    Serial.println(total);
    delay(100);
}


void EnterMotorMode() {
    byte buf[8] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC};
    CAN.sendMsgBuf(0x15, 0, 8, buf);
}

void ExitMotorMode() {
    byte buf[8] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD};
    CAN.sendMsgBuf(0x15, 0, 8, buf);
}

void Zero() {
    byte buf[8] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE};
    CAN.sendMsgBuf(0x15, 0, 8, buf);
}

void pack_cmd() {
    byte buf[8];

    float p_des = constrain(p_in, P_MIN, P_MAX);
    float v_des = constrain(v_in, V_MIN, V_MAX);
    float kp = constrain(kp_in, KP_MIN, KP_MAX);
    float kd = constrain(kd_in, KD_MIN, KD_MAX);
    float t_ff = constrain(t_in, T_MIN, T_MAX);

    unsigned int p_int = float_to_uint(p_des, P_MIN, P_MAX, 16);
    unsigned int v_int = float_to_uint(v_des, V_MIN, V_MAX, 12);
    unsigned int kp_int = float_to_uint(kp, KP_MIN, KP_MAX, 12);
    unsigned int kd_int = float_to_uint(kd, KD_MIN, KD_MAX, 12);
    unsigned int t_int = float_to_uint(t_ff, T_MIN, T_MAX, 12);

    buf[0] = p_int >> 8;                                       
    buf[1] = p_int & 0xFF;
    buf[2] = v_int >> 4;
    buf[3] = ((v_int & 0xF) << 4) | (kp_int >> 8);
    buf[4] = kp_int & 0xFF;
    buf[5] = kd_int >> 4;
    buf[6] = ((kd_int & 0xF) << 4) | (t_int >> 8);
    buf[7] = t_int & 0xFF;

    CAN.sendMsgBuf(0x15, 0, 8, buf);
}

void unpack_reply() {
    byte len = 0;
    byte buf[8];
    CAN.readMsgBuf(&len, buf);

    unsigned int p_int = (buf[1] << 8) | buf[2];
    unsigned int v_int = (buf[3] << 4) | (buf[4] >> 4);
    unsigned int i_int = ((buf[4] & 0xF) << 8) | buf[5];

    p_out = uint_to_float(p_int, P_MIN, P_MAX, 16);
    v_out = uint_to_float(v_int, V_MIN, V_MAX, 12);
    t_out = uint_to_float(i_int, -T_MAX, T_MAX, 12);
}

unsigned int float_to_uint(float x, float x_min, float x_max, int bits) {
    return (unsigned int)((x - x_min) * ((bits == 12) ? 4095.0 : 65535.0) / (x_max - x_min));
}

float uint_to_float(unsigned int x_int, float x_min, float x_max, int bits) {
    return ((float)x_int) * (x_max - x_min) / ((bits == 12) ? 4095.0 : 65535.0) + x_min;
}
