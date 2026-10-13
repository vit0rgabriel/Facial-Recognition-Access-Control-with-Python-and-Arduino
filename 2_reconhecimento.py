import cv2
import numpy as np
import os
import serial
import time
from pathlib import Path
from collections import deque

# --- CONFIGURAÇÃO DA PORTA SERIAL DO ARDUINO ---
porta_arduino = 'COM5'  # Se mudar no gerenciador, altere aqui (ex: 'COM4')
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

            # Lemos a imagem como bytes puros para evitar erros com acentos na pasta
            dados_imagem = np.fromfile(str(arquivo.resolve()), dtype=np.uint8)
            imagem = cv2.imdecode(dados_imagem, cv2.IMREAD_GRAYSCALE)

            if imagem is not None and imagem.size > 0:
                # 🛠️ CORREÇÃO CRÍTICA: Recuperando o índice [1] do ID da foto corretamente
                id_pessoa = int(partes[1])
                faces.append(imagem)
                labels.append(id_pessoa)
    except Exception as e:
        continue

if len(faces) == 0:
    print("Erro: Nenhuma imagem valida pôde ser lida para realizar o treinamento.")
    print("Verifique se os arquivos dentro de 'fotos_treino' comecam com a palavra 'pessoa'.")
    exit()

labels = np.array(labels)

print("Treinando o modelo de reconhecimento LBPH...")
reconhecedor = cv2.face.LBPHFaceRecognizer_create()
reconhecedor.train(faces, labels)
print("Treinamento concluido com sucesso!")

CADASTRADO_OPENCV = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
classificador = cv2.CascadeClassifier(CADASTRADO_OPENCV)

# --- INICIALIZAÇÃO DIRETA DA CÂMERA ---
print("Iniciando sua webcam...")
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    camera.release()
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not camera.isOpened():
    camera.release()
    camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("\n[ERRO CRÍTICO]: Nao foi possivel abrir a sua camera.")
    if conexao_arduino:
        conexao_arduino.close()
    exit()

# --- CONFIGURAÇÃO DOS USUÁRIOS DO GRUPO ---
ids_autorizados = [1, 2]
nomes = {
    1: "Vitor",
    2: "Nathan"
}

# Histórico para o filtro de estabilização de imagem
historico_reconhecimento = deque(maxlen=10)

ultimo_envio = 0
ultimo_comando = None
intervalo_envio = 6  # so limita a REPETICAO do mesmo comando; comando novo sai na hora

# --- LOOP PRINCIPAL DO SISTEMA ---
while True:
    print("monitorando...")

    sucesso, frame = camera.read()
    if not sucesso:
        print("Erro: Nao foi possivel acessar o frame da camera.")
        break

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador.detectMultiScale(cinza, scaleFactor=1.08, minNeighbors=8)

    tempo_atual = time.time()

    if len(rostos) == 0:
        if len(historico_reconhecimento) > 0:
            historico_reconhecimento.popleft()

    for (x, y, w, h) in rostos:
        rosto_cortado = cinza[y:y + h, x:x + w]
        rosto_redimensionado = cv2.resize(rosto_cortado, (100, 100))

        id_previsto, confianca = reconhecedor.predict(rosto_redimensionado)

        # Usando limite equilibrado em 82 para o filtro atuar com estabilidade
        if confianca < 82 and id_previsto in ids_autorizados:
            historico_reconhecimento.append(id_previsto)
        else:
            historico_reconhecimento.append(-1)

        contagem_vitor = historico_reconhecimento.count(1)
        contagem_nathan = historico_reconhecimento.count(2)

        if contagem_vitor >= 6:
            nome = nomes[1]
            cor = (0, 255, 0)
            autorizado = True
        elif contagem_nathan >= 6:
            nome = nomes[2]
            cor = (0, 255, 0)
            autorizado = True
        else:
            nome = "Desconhecido / Bloqueado"
            cor = (0, 0, 255)
            autorizado = False

        if autorizado:
            print("\n=============================================")
            print(f"   ACESSO LIBERADO: BEM-VINDO, {nome.upper()}!   ")
            print("=============================================\n")

            if conexao_arduino and (ultimo_comando != b'1' or tempo_atual - ultimo_envio > intervalo_envio):
                try:
                    conexao_arduino.write(b'1')
                    ultimo_envio = tempo_atual
                    ultimo_comando = b'1'
                except Exception:
                    pass
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("   ALERTA: ACESSO NEGADO / ALVO BLOQUEADO    ")
            print("   USUARIO NAO RECONHECIDO NO BANCO DE DADOS ")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

            # So nega depois que o historico encheu, para nao mandar '0'
            # enquanto o filtro ainda esta reconhecendo uma pessoa autorizada
            filtro_confirmou = len(historico_reconhecimento) == historico_reconhecimento.maxlen

            if conexao_arduino and filtro_confirmou and (ultimo_comando != b'0' or tempo_atual - ultimo_envio > intervalo_envio):
                try:
                    conexao_arduino.write(b'0')
                    ultimo_envio = tempo_atual
                    ultimo_comando = b'0'
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
