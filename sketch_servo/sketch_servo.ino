#include <Servo.h> // Biblioteca nativa para controlar o Servo Motor

// --- DEFINIÇÃO DOS PINOS ---
const int pinoLedVerde    = 2;  // LED que pisca no acesso liberado
const int pinoLedVermelho = 3;  // LED que acende no acesso negado
const int pinoBuzzer      = 4;  // Buzzer para os efeitos sonoros
const int pinoServo       = 5;  // Pino de sinal do Servo Motor

Servo meuServo; 

void setup() {
  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  meuServo.attach(pinoServo);

  // Tudo começa desligado e trancado (0 graus)
  digitalWrite(pinoLedVerde, LOW);
  digitalWrite(pinoLedVermelho, LOW);
  digitalWrite(pinoBuzzer, LOW);
  meuServo.write(0); 

  Serial.begin(9600); // Inicializa a comunicação com o Python
}

void loop() {
  if (Serial.available() > 0) {
    char sinalRecebido = Serial.read(); 

    // --- CASO 1: VITOR OU NATHAN RECONHECIDOS (Sinal '1') ---
    if (sinalRecebido == '1') {
      meuServo.write(90); // Gira o servo para abrir a tranca

      // Efeito Sonoro Alegre (Bip Duplo Rápido e Agudo: Bip-Bip!)
      tone(pinoBuzzer, 1500);            // Som agudo
      digitalWrite(pinoLedVerde, HIGH);  // Acende LED Verde
      delay(150);
      noTone(pinoBuzzer);
      digitalWrite(pinoLedVerde, LOW);   // Apaga LED Verde (efeito pisca)
      delay(100);
      
      tone(pinoBuzzer, 1800);            // Som mais agudo ainda
      digitalWrite(pinoLedVerde, HIGH);  // Pisca o LED Verde de novo
      delay(150);
      noTone(pinoBuzzer);
      digitalWrite(pinoLedVerde, LOW);

      delay(4000); // Mantém a porta aberta por 4 segundos
      meuServo.write(0); // Tranca novamente
    }

    // --- CASO 2: DESCONHECIDO DETECTADO (Sinal '0') ---
    else if (sinalRecebido == '0') {
      meuServo.write(0); // Garante que continua trancado
      digitalWrite(pinoLedVermelho, HIGH); // Acende o LED Vermelho Fixo

      // Efeito Sonoro de Alerta (Som Grave, Longo e Contínuo: Bzzzzt!)
      tone(pinoBuzzer, 400); // Som bem grave de erro
      delay(800);            // Mantém o barulho por quase 1 segundo
      noTone(pinoBuzzer);    

      digitalWrite(pinoLedVermelho, LOW); // Apaga o LED Vermelho
    }
  }
}
