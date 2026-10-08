// Pinos de hardware
const int pinoRele = 7;     // Conectado ao pino de sinal IN do Relé
const int ledVerde = 8;     // LED de acesso liberado
const int ledVermelho = 9;  // LED de acesso negado

void setup() {
  Serial.begin(9600); // Inicializa a comunicação serial a 9600 bps
  
  pinMode(pinoRele, OUTPUT);
  pinMode(ledVerde, OUTPUT);0
  pinMode(ledVermelho, OUTPUT);
  
  // Estado inicial: Trava trancada, LED vermelho aceso
  digitalWrite(pinoRele, LOW); // Relé desligado (trava fechada)
  digitalWrite(ledVerde, LOW);
  digitalWrite(ledVermelho, HIGH);
}

void loop() {
  // Verifica se há dados recebidos pela porta Serial
  if (Serial.available() > 0) {
    char comando = Serial.read(); // Lê o caractere enviado pelo Python
    
    if (comando == '1') {
      // ACESSO LIBERADO: Abre a trava por 5 segundos
      digitalWrite(ledVermelho, LOW);
      digitalWrite(ledVerde, HIGH);
      digitalWrite(pinoRele, HIGH); // Ativa o relé (destranca)
      
      delay(5000); // Mantém aberto por 5 segundos
      
      // Volta ao estado trancado
      digitalWrite(pinoRele, LOW);
      digitalWrite(ledVerde, LOW);
      digitalWrite(ledVermelho, HIGH);
    } 
    else if (comando == '0') {
      // ACESSO NEGADO
      digitalWrite(pinoRele, LOW);
      digitalWrite(ledVerde, LOW);
      digitalWrite(ledVermelho, HIGH);
    }
  }
}