# -*- coding: utf-8 -*-
"""
versão: 17012025v3
autor: Rafael L
"suporte" e consulta: GPT4o-mini (acabei usando)

Colaboradores: Churubim Productions 
"""

#Imports________________________________________
import RPi.GPIO as GPIO
import time
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import spi
from luma.lcd.device import st7789
#________________________________________________

# Configuracao do display SPI 1.3" ST7789 _______________________
serial = spi(device=0, port=0, gpio_DC=24, gpio_RST=25, gpio_CS=8)

disp = st7789(serial, width=240, height=240)
#________________________________________________________________

# Configuracao de pinos para os botoes___________________________
BOT_OK = 17                      #Obturador e OK
BOT_ISO_OBT_UP = 27              #ISO e Vel.Obturador +
BOT_ISO_OBT_DOWN = 23            #ISO e Vel.Obturador -
BOT_MENU_VOLTAR = 5              #Menu e Voltar
BOT_TROCA_EXCL = 6               #Troca ISO/Obt. e Excluir

# Configuracao dos botoes GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BOT_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_ISO_OBT_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_ISO_OBT_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_MENU_VOLTAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_TROCA_EXCL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#_________________________________________________________________

# Inicializacao das variaveis_____________________________________
val_ISOs = [1.0, 2.0, 4.0, 8.0, 16.0] #Na verdade do ganho
val_VelOBT = [1, 2, 3, 4, 5]  # em segundos
ISO_atual = val_ISOs[0]
VelOBT_atual = val_VelOBT[0]
lista_fotos = []         #Iniciando a lista da galeria
val_foto_atual = 0
modo_GALERIA = False
hora_ult_foto = None  # Para determinar a hora da foto
modo_EXCLUIR = False  # Modo para confirmacao de exclusao
#_________________________________________________________________

# Conferindo a pasta das fotos
try:
    pasta_fotos = "DCIM"
    os.makedirs(pasta_fotos, exist_ok=True)
except OSError as e:
    print(f"Erro ao criar a pasta de fotos: {e}")
    exit(1)  # Sai do programa em caso de erro critico

#__________________________________________________________

# Funcao para capturar a foto
def tira_foto():
    global hora_ult_foto
    # Gerar nome da foto com a data e hora
    data_ext = datetime.now()
    nomefoto = f"DCIM/photo_{data_ext.strftime('%Y%m%d_%H%M%S')}.jpg"
    
    # Comando para capturar a imagem com o libcamera usando ISO e Vel. Obturador
    subprocess.run(f"libcamera-still -o {nomefoto} --width 2592 --height 1944 --shutter {VelOBT_atual * 1000000} --gain {ISO_atual:.1f} --awbgains 1.2,1.2 --immediate --denoise off --nopreview", shell=True)
    
    # Salva na galeria
    lista_fotos.append(nomefoto) #Lista para acompanhar o que o usuario veê
    val_foto_atual = len(lista_fotos) - 1
    hora_ult_foto = data_ext
    print(f"Foto capturada: {nomefoto}")
    
    time.sleep(1)
    # Exibir preview da foto no display por 4 segundos
    img = Image.open(nomefoto)
    img = img.resize((disp.width, disp.height))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Adicionar data e hora na imagem no rodapé
    timestamp = data_ext.strftime('%Y-%m-%d %H:%M:%S')
    draw.text((10, img.height - 20), f"Data: {timestamp}", font=font, fill="yellow")
    img.save(nomefoto)
    
    disp.display(img)
    time.sleep(4)
    disp.clear()

# Funcao para exibir o ISO e Vel. Obturador na tela durante a captura
def mostra_val():
    img = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype("Fontes/DS-DIGII.TTF", 22)

    # Mostrar valores de ISO e Vel. Obturador
    draw.text((10, 10), f"GANHO: {ISO_atual}", font=fonte, fill="yellow")
    draw.text((10, 30), f"Vel. Obturador: {VelOBT_atual} seg", font=fonte, fill="yellow")
    
    disp.display(img)

# Funcao que entrega a lista de fotos
def carregar_fotos():
    fotos = sorted(
        [f for f in os.listdir(pasta_fotos) if f.endswith(".jpg")],
        key=lambda x: os.path.getctime(os.path.join(pasta_fotos, x))
    )
    return fotos

# Funcao para exibir a galeria de fotos
def mostra_galeria():
    global val_foto_atual
    fotos = carregar_fotos()
    
    if fotos:
        val_foto_atual = max(0, min(val_foto_atual, len(fotos) - 1))  # Garantir que o indice esteja valido
        caminho_foto = os.path.join(pasta_fotos, fotos[val_foto_atual])
        
        img = Image.open(caminho_foto).resize((disp.width, disp.height))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        # Mostrar nome e data
        timestamp = datetime.fromtimestamp(os.path.getctime(caminho_foto)).strftime('%Y-%m-%d %H:%M:%S')
        draw.text((10, img.height - 20), f"Data: {timestamp}", font=font, fill="yellow")
        
        disp.display(img)

# Funcao para excluir a foto
def excluir_foto():
    global lista_fotos, val_foto_atual, modo_EXCLUIR
    if lista_fotos and modo_EXCLUIR:
        foto_a_excluir = lista_fotos[val_foto_atual]  # Obter o caminho da foto
        os.remove(foto_a_excluir)  # Remove o arquivo
        lista_fotos.pop(val_foto_atual)  # Remove da lista
        print(f"Foto excluida: {foto_a_excluir}")
        
        # Ajusta o indice para evitar valores fora do intervalo
        if val_foto_atual >= len(lista_fotos):
            val_foto_atual = max(0, len(lista_fotos) - 1)
        
        # Atualiza a galeria ou limpa a tela se nao houver mais fotos
        if lista_fotos:
            mostra_galeria()
        else:
            disp.clear()  # Limpa o display se nao houver mais fotos
            print("Nenhuma foto restante.")
        
        modo_EXCLUIR = False  # Sai do modo de exclusao


# Funcao para manipular ISO e Vel. Obturador
def mais_ISO_VelOBT():
    global ISO_atual, VelOBT_atual
    if sw_ISO_VelOBT:  # Alterna para ISO
        ISO_atual = val_ISOs[(val_ISOs.index(ISO_atual) + 1) % len(val_ISOs)]
    else:  # Alterna para Vel. Obturador
        VelOBT_atual = val_VelOBT[(val_VelOBT.index(VelOBT_atual) + 1) % len(val_VelOBT)]

def menos_ISO_VelOBT():
    global ISO_atual, VelOBT_atual
    if sw_ISO_VelOBT:  # Alterna para ISO
        ISO_atual = val_ISOs[(val_ISOs.index(ISO_atual) - 1) % len(val_ISOs)]
    else:  # Alterna para Vel. Obturador
        VelOBT_atual = val_VelOBT[(val_VelOBT.index(VelOBT_atual) - 1) % len(val_VelOBT)]

# Funcao para alternar entre ISO e Vel. Obturador
def alternar_ISO_VelOBT():
    global sw_ISO_VelOBT
    sw_ISO_VelOBT = not sw_ISO_VelOBT


# Funcao para mostrar aviso de exclusao
def mostra_ALERTA_excluir():
    disp.clear()
    font = ImageFont.load_default()
    img_ALERTA = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img_ALERTA)
    draw.text((10, 10), "Aperte OK para confirmar", font=font, fill="yellow")
    disp.display(img_ALERTA)
    
# Funcao para desligar o sistema
def desliga_sistema():
    fonte = ImageFont.truetype("Fontes/DS-DIGII.TTF", 22)
    disp.clear()  # Limpa o display
    img_desligar = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img_desligar)
    font = ImageFont.load_default()
    draw.text((10, 10), "Desligando...", font=fonte, fill="yellow")
    disp.display(img_desligar)
    time.sleep(2)  # Exibe a mensagem por 2 segundos
    os.system("sudo shutdown now")  # Envia o comando para desligar

# Loop principal_______________________________________________________________
sw_ISO_VelOBT = True
try:
    while True:
        # Exibir configuracoes de captura no modo de captura
        if not modo_GALERIA:
            mostra_val()

        # Verifica os botoes
        if GPIO.input(BOT_OK) == GPIO.LOW:
            if modo_GALERIA:
                if modo_EXCLUIR:
                    excluir_foto()  # Exclui a foto na galeria
            else:
                tira_foto()  # Captura a foto
                time.sleep(0.2)
        
        if GPIO.input(BOT_ISO_OBT_UP) == GPIO.LOW and modo_GALERIA:
            val_foto_atual += 1  # Proxima foto
            mostra_galeria()
            time.sleep(0.2)
        
        if GPIO.input(BOT_ISO_OBT_DOWN) == GPIO.LOW and modo_GALERIA:
            val_foto_atual -= 1  # Foto anterior
            mostra_galeria()
            time.sleep(0.2)
        
        if GPIO.input(BOT_MENU_VOLTAR) == GPIO.LOW:
            if modo_EXCLUIR:  # Se estiver no modo de exclusao
                modo_EXCLUIR = False  # Cancela o modo de exclusao
                mostra_galeria()  # Volta para a galeria
            else:
                # Alterna entre o modo de captura e galeria, comportamento atual
                modo_GALERIA = not modo_GALERIA
                if modo_GALERIA:
                    mostra_galeria()
                else:
                    disp.clear()
            time.sleep(0.2)
        
        if GPIO.input(BOT_TROCA_EXCL) == GPIO.LOW:
            if modo_GALERIA:
                mostra_ALERTA_excluir()  # Exibe a mensagem de alerta
                modo_EXCLUIR = True
                time.sleep(0.5)
            alternar_ISO_VelOBT()  # Alterna entre ISO e Vel. Obturador
            time.sleep(0.2)
            
        if GPIO.input(BOT_MENU_VOLTAR) == GPIO.LOW and GPIO.input(BOT_TROCA_EXCL) == GPIO.LOW:
            desliga_sistema()
            break

except KeyboardInterrupt:
    GPIO.cleanup()

