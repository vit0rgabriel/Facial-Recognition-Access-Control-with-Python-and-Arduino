import cv2
import os

# Configuração do detector de rostos e da câmera
CADASTRADO_OPENCV = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
classificador = cv2.CascadeClassifier(CADASTRADO_OPENCV)

print("Tentando conectar com a webcam...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    camera = cv2.VideoCapture(1)

if not camera.isOpened():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("\n[ERRO]: Não foi possível ligar a sua webcam em nenhum canal USB.")
    exit()

# ID do usuário (Ex: 1 para Pessoa A, 2 para Pessoa B)
id_usuario = input("\nDigite o ID numérico do usuário (ex: 1): ")
amostras = 1
max_amostras = 25  # Número de fotos a capturar

# Criar pasta para armazenar as fotos se não existir
if not os.path.exists("fotos_treino"):
    os.makedirs("fotos_treino")

print("Olhe para a câmera. Capturando fotos...")

while True:
    sucesso, frame = camera.read()
    if not sucesso:
        print("Erro: Não foi possível ler a imagem da câmera.")
        break

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 🛠️ CORREÇÃO CRÍTICA AQUI: Mudei minNeighbors para 9 e ajustado scaleFactor para 1.15
    # Isso elimina falsos positivos da parede e melhora a precisão drasticamente
    rostos = classificador.detectMultiScale(cinza, scaleFactor=1.15, minNeighbors=9)

    for (x, y, w, h) in rostos:
        # Cortar e redimensionar o rosto exatamente para 100x100
        rosto_cortado = cinza[y:y + h, x:x + w]
        rosto_redimensionado = cv2.resize(rosto_cortado, (100, 100))

        # Salvar o arquivo formatado: pessoa.ID.AMOSTRA.jpg
        caminho_foto = f"fotos_treino/pessoa.{id_usuario}.{amostras}.jpg"
        cv2.imwrite(caminho_foto, rosto_redimensionado)

        # Desenhar retângulo na tela para retorno visual
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print(f"Foto {amostras} salva com sucesso!")
        amostras += 1

    cv2.imshow("Capturando Rostos - Pressione ESC para sair", frame)

    if cv2.waitKey(100) & 0xFF == 27 or amostras > max_amostras:
        break

camera.release()
cv2.destroyAllWindows()
print(f"Fotos capturadas com sucesso para o ID {id_usuario}!")
