#include <Servo.h> // Biblioteca nativa para controlar o Servo Motor

// --- DEFINIÇÃO DOS PINOS ---
const int pinoLedVerde    = 2;  // LED que pisca no acesso liberado
const int pinoLedVermelho = 3;  // LED que acende no acesso negado
const int pinoBuzzer      = 4;  // Buzzer para os efeitos sonoros
const int pinoServo       = 5;  // Pino de sinal do Servo Motor (Fio Laranja)

Servo meuServo; // Cria o objeto para controlar o servo

void setup() {
  // Configura os pinos como saídas do Arduino
  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  // Inicializa o servo no pino correto
  meuServo.attach(pinoServo);

  // Garante que tudo comece desligado e a trava comece TRANCADA (0 graus)
  digitalWrite(pinoLedVerde, LOW);
  digitalWrite(pinoLedVermelho, LOW);
  digitalWrite(pinoBuzzer, LOW);
  meuServo.write(0); // 0 graus = Posição Trancada

  // Inicializa a comunicação Serial a 9600 baud (mesma velocidade do Python)
  Serial.begin(9600);
}

void loop() {
  // Verifica se o Python enviou algum caractere pela porta serial
  if (Serial.available() > 0) {
    char sinalRecebido = Serial.read(); // Lê o byte enviado

    // --- CASO 1: ACESSO LIBERADO (Python enviou '1') ---
    if (sinalRecebido == '1') {
      // 1. Gira o Servo Motor para a posição aberta (90 graus)
      meuServo.write(90); 

      // 2. Efeito Sonoro Alegre (Bip Duplo Rápido e Agudo) + Pisca LED Verde
      tone(pinoBuzzer, 1500); 
      digitalWrite(pinoLedVerde, HIGH); 
      delay(150);
      noTone(pinoBuzzer);
      digitalWrite(pinoLedVerde, LOW);  
      delay(100);
      
      tone(pinoBuzzer, 1800); 
      digitalWrite(pinoLedVerde, HIGH); 
      delay(150);
      noTone(pinoBuzzer);
      digitalWrite(pinoLedVerde, LOW);

      // 3. Mantém a tranca aberta por 4 segundos para a pessoa passar
      delay(4000); 

      // 4. Move o Servo de volta para fechar a trava (0 graus)
      meuServo.write(0); 
    }

    // --- CASO 2: ACESSO NEGADO / DESCONHECIDO (Python enviou '0') ---
    else if (sinalRecebido == '0') {
      // 1. Garante que o servo continua na posição trancada (0 graus)
      meuServo.write(0); 

      // 2. Acende o LED Vermelho fixo
      digitalWrite(pinoLedVermelho, HIGH);

      // 3. Efeito Sonoro de Alerta (Som Grave, Longo e Contínuo)
      tone(pinoBuzzer, 400); // Som grave de erro (400Hz)
      delay(800);            // Mantém o barulho por quase 1 segundo
      noTone(pinoBuzzer);    // Desliga o som

      // 4. Apaga o LED Vermelho
      digitalWrite(pinoLedVermelho, LOW);
    }
  }
}
