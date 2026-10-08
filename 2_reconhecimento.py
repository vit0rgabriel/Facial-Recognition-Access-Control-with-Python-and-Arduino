import cv2
import numpy as np
import os
import serial
import time
from pathlib import Path

# --- CONFIGURAÇÃO DA PORTA SERIAL DO ARDUINO ---
porta_arduino = 'COM3'
baud_rate = 9600

try:
    conexao_arduino = serial.Serial(porta_arduino, baud_rate, timeout=0.05, write_timeout=0.05)
    time.sleep(2)
    print(f"Conectado ao Arduino na porta {porta_arduino}")
except Exception as e:
    print(f"\n[AVISO]: Nao foi possivel conectar ao Arduino na porta {porta_arduino}.")
    print("O sistema funcionara em MODO LOCAL (apenas na tela).")
    print(f"Erro detalhado: {e}\n")
    conexao_arduino = None

# --- DESCOBRIR CAMINHO DA PASTA DE FOTOS AUTOMATICAMENTE ---
diretorio_atual = Path(__file__).parent.resolve()
pasta_fotos = diretorio_atual / "fotos_treino"

if not pasta_fotos.exists() or len(os.listdir(pasta_fotos)) == 0:
    pasta_fotos = Path("fotos_treino").resolve()

if not pasta_fotos.exists() or len(os.listdir(pasta_fotos)) == 0:
    print(f"Erro: A pasta 'fotos_treino' esta vazia ou nao existe. Rode o script de captura primeiro!")
    exit()

faces = []
labels = []

print("Carregando banco de imagens de forma segura...")
for arquivo in pasta_fotos.glob("*.jpg"):
    try:
        nome_arquivo = arquivo.name

        if nome_arquivo.startswith("pessoa"):
            partes = nome_arquivo.split(".")

            dados_imagem = np.fromfile(str(arquivo.resolve()), dtype=np.uint8)
            imagem = cv2.imdecode(dados_imagem, cv2.IMREAD_GRAYSCALE)

            if imagem is not None and imagem.size > 0:
                id_pessoa = int(partes[1])
                faces.append(imagem)
                labels.append(id_pessoa)
    except Exception as e:
        continue

if len(faces) == 0:
    print("Erro: Nenhuma imagem valida pôde ser lida para realizar o treinamento.")
    exit()

labels = np.array(labels)

print("Treinando o modelo de reconhecimento LBPH...")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.train(faces, labels)
print("Treinamento concluido com sucesso!")

CADASTRADO_OPENCV = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
classificador = cv2.CascadeClassifier(CADASTRADO_OPENCV)

# --- INICIALIZAÇÃO DE CÂMERA ---
print("Buscando sua webcam externa nos canais do Windows...")
camera = None
configuracoes_camera = [
    (0, cv2.CAP_DSHOW),
    (1, cv2.CAP_DSHOW),
    (0, None),
    (1, None)
]

for indice, driver in configuracoes_camera:
    if driver is not None:
        camera = cv2.VideoCapture(indice, driver)
    else:
        camera = cv2.VideoCapture(indice)

    if camera.isOpened():
        sucesso, teste_frame = camera.read()
        if sucesso:
            print(f"Webcam ativada com sucesso no indice {indice}!")
            break
        camera.release()
    else:
        camera.release()

if camera is None or not camera.isOpened():
    print("\n[ERRO CRÍTICO]: Nao foi possivel abrir a sua camera.")
    exit()

# --- CONFIGURAÇÃO DOS USUÁRIOS DO GRUPO ---
ids_autorizados = [1, 2]
nomes = {
    1: "Vitor",
    2: "Nathan"
}

ultimo_envio = 0
intervalo_envio = 6

# --- LOOP PRINCIPAL DO SISTEMA ---
while True:
    print("monitorando...")

    sucesso, frame = camera.read()
    if not sucesso:
        print("Erro: Nao foi possivel acessar o frame da camera.")
        break

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecção equilibrada e suave para evitar variações bruscas
    rostos = classificador.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=8)

    tempo_atual = time.time()

    for (x, y, w, h) in rostos:
        rosto_cortado = cinza[y:y + h, x:x + w]
        rosto_redimensionado = cv2.resize(rosto_cortado, (100, 100))

        # Equaliza o histograma do rosto capturado para corrigir variações de luz
        rosto_equalizado = cv2.equalizeHist(rosto_redimensionado)

        id_previsto, confianca = reconhecedor.predict(rosto_equalizado)

        # 🛠️ AJUSTE PERFEITO: Limite em 90 para te dar tolerância à iluminação sem liberar invasores
        if confianca < 90 and id_previsto in ids_autorizados:
            nome = nomes.get(id_previsto, f"ID {id_previsto}")
            cor = (0, 255, 0)  # Verde

            print("\n=============================================")
            print(f"   ACESSO LIBERADO: BEM-VINDO, {nome.upper()}!   ")
            print("=============================================\n")

            if conexao_arduino and (tempo_atual - ultimo_envio > intervalo_envio):
                try:
                    conexao_arduino.write(b'1')
                    ultimo_envio = tempo_atual
                except Exception:
                    pass
        else:
            nome = "Desconhecido / Bloqueado"
            cor = (0, 0, 255)  # Vermelho

            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("   ALERTA: ACESSO NEGADO / ALVO BLOQUEADO    ")
            print("   USUARIO NAO RECONHECIDO NO BANCO DE DADOS ")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

            if conexao_arduino and (tempo_atual - ultimo_envio > intervalo_envio):
                try:
                    conexao_arduino.write(b'0')
                    ultimo_envio = tempo_atual
                except Exception:
                    pass

        cv2.rectangle(frame, (x, y), (x + w, y + h), cor, 2)
        cv2.putText(frame, f"{nome} ({int(confianca)})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

    cv2.imshow("Reconhecimento Facial + Arduino", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()

if conexao_arduino:
    try:
        conexao_arduino.close()
    except Exception:
        pass
print("Programa finalizado.")
