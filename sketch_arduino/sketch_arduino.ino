#include <Servo.h>

// --- MAPEAMENTO EXATO DA SUA IMAGEM + BUZZER ---
const int pinoLedAmarelo  = 2;  // Fio Amarelo -> LED Amarelo (Monitorando)
const int pinoLedVerde    = 3;  // Fio Verde   -> LED Verde (Acesso Liberado)
const int pinoLedVermelho = 4;  // Fio Azul    -> LED Vermelho (Acesso Negado)
const int pinoBuzzer      = 6;  // Cabo no F6  -> Buzzer Passivo (F10 vai no GND)
const int pinoServo       = 9;  // Fio Laranja -> Servo Motor

Servo meuServo;

void setup() {
  Serial.begin(9600);
  
  // Configura todos os componentes como saídas
  pinMode(pinoLedAmarelo, OUTPUT);
  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);
  
  meuServo.attach(pinoServo);

  // --- ESTADO INICIAL (Ligado e Monitorando) ---
  meuServo.write(0);                    // Começa trancado (0 graus)
  digitalWrite(pinoLedVerde, LOW);      // Verde apagado
  digitalWrite(pinoLedVermelho, LOW);   // Vermelho apagado
  digitalWrite(pinoLedAmarelo, HIGH);   // Amarelo ACESO indicando que está monitorando
}

void loop() {
  // Verifica se o Python enviou algum comando
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    // --- CASO 1: ACESSO LIBERADO (Python enviou '1') ---
    if (comando == '1') {
      digitalWrite(pinoLedAmarelo, LOW);  // Apaga o amarelo de espera
      digitalWrite(pinoLedVermelho, LOW); // Garante que o vermelho está apagado
      digitalWrite(pinoLedVerde, HIGH);   // Acende o Verde de sucesso
      
      meuServo.write(90);                 // Abre o servo tranca

      // 🔊 Som Alegre no Buzzer Passivo (Bip Duplo Agudo)
      tone(pinoBuzzer, 1500, 150);        // Nota de 1500Hz por 150 milissegundos
      delay(200);                         // Pausa entre os bipes
      tone(pinoBuzzer, 1800, 150);        // Nota de 1800Hz por 150 milissegundos

      delay(4000);                        // Mantém a porta aberta por 4 segundos

      // Voltar ao estado de monitoramento após o tempo
      meuServo.write(0);                  // Tranca o servo de novo
      digitalWrite(pinoLedVerde, LOW);    // Apaga o Verde
      digitalWrite(pinoLedAmarelo, HIGH); // Reativa o Amarelo (Voltando a monitorar...)
    } 
    
    // --- CASO 2: ACESSO NEGADO / DESCONHECIDO (Python enviou '0') ---
    else if (comando == '0') {
      digitalWrite(pinoLedAmarelo, LOW);    // Apaga o amarelo
      digitalWrite(pinoLedVerde, LOW);      // Garante que o verde está apagado
      digitalWrite(pinoLedVermelho, HIGH);  // Acende o Vermelho de Alerta

      meuServo.write(0);                    // Garante que a tranca continue fechada

      // 🔊 Som de Erro no Buzzer Passivo (Som Grave e Longo)
      tone(pinoBuzzer, 350, 800);           // Nota bem grave de 350Hz por 800 milissegundos
      delay(850);                           // Aguarda o tempo do som terminar

      digitalWrite(pinoLedVermelho, LOW);   // Apaga o Vermelho após o alarme
      digitalWrite(pinoLedAmarelo, HIGH);   // Volta o Amarelo para continuar monitorando
    }
  }
}
