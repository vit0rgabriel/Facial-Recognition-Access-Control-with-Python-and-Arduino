// Fechadura com reconhecimento facial
// Recebe comandos do teste.py pela porta serial (9600 baud):
//   '1' -> acesso liberado  (abre a trava, LED verde, bip curto)
//   '0' -> acesso negado    (LED vermelho, bip longo)

#include <Servo.h>

// --- PINOS ---
const int PINO_SERVO     = 2;
const int PINO_RELE      = 7;   // use se a trava for solenoide (via modulo rele)
const int PINO_LED_VERDE = 4;
const int PINO_LED_VERM  = 3;
const int PINO_BUZZER    = 5;

// --- AJUSTES ---
const int ANGULO_FECHADO = 0;   // travado (calibrado)
const int ANGULO_ABERTO  = 90;  // destravado (calibrado)
const unsigned long TEMPO_ABERTO = 3000;  // ms que o servo fica aberto e o LED verde aceso
const unsigned long TEMPO_ALERTA = 2000;  // ms do LED vermelho aceso

Servo trava;
unsigned long abriuEm = 0;
unsigned long alertaEm = 0;
bool aberta = false;
bool alerta = false;

void setup() {
  Serial.begin(9600);

  pinMode(PINO_RELE, OUTPUT);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_VERM, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);

  trava.attach(PINO_SERVO);
  fechar();

  Serial.println("Arduino pronto");
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') {
      abrir();
    } else if (comando == '0') {
      negar();
    }
    // outros caracteres (ex: '\n') sao ignorados
  }

  // Fecha automaticamente depois de TEMPO_ABERTO, sem travar o loop com delay()
  if (aberta && millis() - abriuEm >= TEMPO_ABERTO) {
    fechar();
  }

  if (alerta && millis() - alertaEm >= TEMPO_ALERTA) {
    digitalWrite(PINO_LED_VERM, LOW);
    alerta = false;
  }
}

void abrir() {
  trava.write(ANGULO_ABERTO);
  digitalWrite(PINO_RELE, HIGH);
  digitalWrite(PINO_LED_VERDE, HIGH);
  digitalWrite(PINO_LED_VERM, LOW);
  alerta = false;
  tone(PINO_BUZZER, 2000, 150);

  aberta = true;
  abriuEm = millis();
  Serial.println("ACESSO LIBERADO");
}

void fechar() {
  trava.write(ANGULO_FECHADO);
  digitalWrite(PINO_RELE, LOW);
  digitalWrite(PINO_LED_VERDE, LOW);
  aberta = false;
}

void negar() {
  if (aberta) return;  // nao interrompe uma liberacao em andamento

  digitalWrite(PINO_LED_VERM, HIGH);
  tone(PINO_BUZZER, 400, 600);

  alerta = true;
  alertaEm = millis();
  Serial.println("ACESSO NEGADO");
}