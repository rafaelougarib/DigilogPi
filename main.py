# -*- coding: utf-8 -*-
"""
Editado usando o desconhecido (mas muito bão) Spyder :)

versão: 16012025v1
autor: Rafael L
"suporte" e consulta: GPT4o-mini (acabei usando)

"""


import RPi.GPIO as GPIO
import time
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import spi
from luma.lcd.device import st7789

# Configuração do display SPI 1.3" ST7789
serial = spi(device=0, port=0, gpio_DC=24, gpio_RST=25, gpio_CS=8)

disp = st7789(serial, width=240, height=240)

# Configuração de pinos para os botões
BOT_OK = 17                      #Obturador e OK
BOT_ISO_OBT_UP = 27              #ISO e Vel.Obturador +
BOT_ISO_OBT_DOWN = 23            #ISO e Vel.Obturador -
BOT_MENU_VOLTAR = 5              #Menu e Voltar
BOT_TROCA_EXCL = 6               #Troca ISO/Obt. e Excluir

# Configuração dos botões GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BOT_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_ISO_OBT_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_ISO_OBT_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_MENU_VOLTAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOT_TROCA_EXCL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicialização das variáveis
val_ISOs = [1.0, 2.0, 4.0, 8.0, 16.0] #Na verdade do ganho, libcamera não possuia --iso
val_VelOBT = [1, 2, 3, 4, 5]  # em segundos
ISO_atual = val_ISOs[0]
VelOBT_atual = val_VelOBT[0]
lista_fotos = []         #Iniciando a lista da galeria
val_foto_atual = 0
modo_GALERIA = False
hora_ult_foto = None  # Para determinar a hora da foto
modo_EXCLUIR = False  # Modo para confirmação de exclusão

#__________________________________________________________

# Funcao para capturar a foto
def tira_foto():
    global hora_ult_foto
    # Gerar nome da foto com a data e hora
    data_ext = datetime.now()
    nomefoto = f"photo_{data_ext.strftime('%Y%m%d_%H%M%S')}.jpg"
    
    # Comando para capturar a imagem com o libcamera usando ISO e Vel. Obturador
    subprocess.run(f"libcamera-still -o {nomefoto} --width 2592 --height 1944 --shutter {VelOBT_atual * 1000000} --gain {ISO_atual:.1f} --awbgains 1.2,1.2 --immediate --denoise off --nopreview", shell=True)
    
    # Salva na galeria
    lista_fotos.append(nomefoto) #Lista para acompanhar o que o usuario vê
    val_foto_atual = len(lista_fotos) - 1
    hora_ult_foto = data_ext
    print(f"Foto capturada: {nomefoto}")
    
    time.sleep(1+VelOBT_atual)
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

# Função para exibir o ISO e Vel. Obturador na tela durante a captura
def mostra_val():
    img = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype("Fontes/DS-DIGII.TTF", 20)

    # Mostrar valores de ISO e Vel. Obturador
    draw.text((10, 10), f"GANHO: {ISO_atual}", font=fonte, fill="yellow")
    draw.text((10, 30), f"Vel. Obturador: {VelOBT_atual} seg", font=fonte, fill="yellow")
    
    disp.display(img)

# Função para exibir a galeria de fotos
def mostra_galeria():
    global val_foto_atual
    if lista_fotos:
        img = Image.open(lista_fotos[val_foto_atual])
        img = img.resize((disp.width, disp.height))
        
        # Exibir nome ou data da foto no rodapé
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        timestamp = datetime.fromtimestamp(os.path.getctime(lista_fotos[val_foto_atual])).strftime('%Y-%m-%d %H:%M:%S')
        draw.text((10, img.height - 20), f"Nome: {timestamp}", font=font, fill="yellow")
        
        disp.display(img)

# Função para excluir a foto
def excluir_foto():
    global lista_fotos, val_foto_atual
    if lista_fotos and modo_EXCLUIR:
        os.remove(lista_fotos[val_foto_atual])
        lista_fotos.pop(val_foto_atual)
        val_foto_atual = min(val_foto_atual, len(lista_fotos) - 1)
        print(f"Foto excluída: {lista_fotos[val_foto_atual]}")
        if lista_fotos:
            mostra_galeria()

# Função para manipular ISO e Vel. Obturador
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

# Função para alternar entre ISO e Vel. Obturador
def alternar_ISO_VelOBT():
    global sw_ISO_VelOBT
    sw_ISO_VelOBT = not sw_ISO_VelOBT


# Função para mostrar aviso de exclusão
def mostra_ALERTA_excluir():
    disp.clear()
    font = ImageFont.load_default()
    img_ALERTA = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img_ALERTA)
    draw.text((10, 10), "Aperte OK para confirmar", font=font, fill="yellow")
    disp.display(img_ALERTA)
    
# Função para desligar o sistema
def desliga_sistema():
    disp.clear()  # Limpa o display
    img_desligar = Image.new('RGB', (disp.width, disp.height), color="black")
    draw = ImageDraw.Draw(img_desligar)
    font = ImageFont.load_default()
    draw.text((10, 10), "Desligando...", font=font, fill="yellow")
    disp.display(img_desligar)
    time.sleep(2)  # Exibe a mensagem por 2 segundos
    os.system("sudo shutdown now")  # Envia o comando para desligar

# Loop principal
sw_ISO_VelOBT = True
try:
    while True:
        # Exibir configurações de captura no modo de captura
        if not modo_GALERIA:
            mostra_val()

        # Verifica os botões
        if GPIO.input(BOT_OK) == GPIO.LOW:
            if modo_GALERIA:
                if modo_EXCLUIR:
                    excluir_foto()  # Exclui a foto na galeria
                    modo_EXCLUIR = False  # Sai do modo de exclusão
                else:
                    # Confirmação de exclusão
                    mostra_ALERTA_excluir()
                    modo_EXCLUIR = True
            else:
                tira_foto()  # Captura a foto
            time.sleep(0.2)
        
        if GPIO.input(BOT_ISO_OBT_UP) == GPIO.LOW:
            mais_ISO_VelOBT()  # Aumenta o ISO ou a velocidade do obturador
            time.sleep(0.2)
        
        if GPIO.input(BOT_ISO_OBT_DOWN) == GPIO.LOW:
            menos_ISO_VelOBT()  # Diminui o ISO ou a velocidade do obturador
            time.sleep(0.2)
        
        if GPIO.input(BOT_MENU_VOLTAR) == GPIO.LOW:
            modo_GALERIA = not modo_GALERIA  # Alterna entre modo de captura e galeria
            if modo_GALERIA:
                mostra_galeria()
            else:
                disp.clear()
            time.sleep(0.2)
        
        if GPIO.input(BOT_TROCA_EXCL) == GPIO.LOW:
            alternar_ISO_VelOBT()  # Alterna entre ISO e Vel. Obturador
            time.sleep(0.2)
            
        if GPIO.input(BOT_MENU_VOLTAR) == GPIO.LOW and GPIO.input(BOT_TROCA_EXCL) == GPIO.LOW:
            desliga_sistema()
            break

except KeyboardInterrupt:
    GPIO.cleanup()

