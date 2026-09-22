import pyautogui
import time
import random
import glob
import os
import ctypes
import threading

from pyautogui import ImageNotFoundException

# Hotkeys globais (Windows) - codigos de virtual-key
VK_SAIR = 0x75    # F6  -> encerra o script
VK_MODO = 0x76    # F7  -> alterna normal <-> grueling
VK_TOGGLE = 0x77  # F8  -> inicia/para

_user32 = ctypes.windll.user32


def tecla_pressionada(vk_code):
    """True se a tecla estiver pressionada agora, mesmo sem foco na janela."""
    return bool(_user32.GetAsyncKeyState(vk_code) & 0x8000)


def encontrar(nome_arquivo_imagem, confianca=0.90, region=None, cinza=True):
    """
    cinza=True  -> compara em preto e branco (mais rapido, ignora cor).
    cinza=False -> compara em RGB. Necessario para distinguir a opcao
                   SELECIONADA (colorida) das nao-selecionadas (dessaturadas).
    """
    try:
        # Retorna o retângulo (left, top, width, height) da imagem
        regiao = pyautogui.locateOnScreen(nome_arquivo_imagem, confidence=confianca, region=region, grayscale=cinza)
        if regiao:
            return True
        else:
            print(f"Não foi possível encontrar a imagem '{nome_arquivo_imagem}' na tela.")
            return False
        
    except ImageNotFoundException:
        #print(f"A imagem '{nome_arquivo_imagem}' não foi encontrada (confiança < {confianca*100:.0f}%).")
        return False
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return False




def encontrar_e_clicar(nome_arquivo_imagem, confianca=0.85, region=None, cinza=True):
    """
    Tenta encontrar uma imagem na tela e clicar em um ponto aleatório dentro dela.
    """

    #print(f"Buscando por '{nome_arquivo_imagem}' com confiança de {confianca*100:.0f}%...")

    try:
        # Retorna o retângulo (left, top, width, height) da imagem
        regiao = pyautogui.locateOnScreen(nome_arquivo_imagem, confidence=confianca, region=region, grayscale=cinza)

        if regiao:
            x, y, largura, altura = regiao
            # Gera coordenadas aleatórias dentro da área da imagem
            #ponto_x = random.randint(x, x + largura - 1)
            #ponto_y = random.randint(y, y + altura - 1)
            
            #pyautogui.moveTo(x, y)
            pyautogui.moveTo(x, y)
            time.sleep(.1)
            pyautogui.click(x, y)
            #print(f"Imagem encontrada e clicada em ponto aleatório: ({ponto_x}, {ponto_y})")
            return True
        else:
            print(f"Não foi possível encontrar a imagem '{nome_arquivo_imagem}' na tela.")
            return False

    except ImageNotFoundException:
        #print(f"A imagem '{nome_arquivo_imagem}' não foi encontrada (confiança < {confianca*100:.0f}%).")
        return False
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return False



# --- Exemplo de uso ---
#time.sleep(5)
#encontrar_e_clicar(
#    r'C:\Users\joaov\Desktop\Codigos\Autoultimatum\images\t03_stormcaller_runes.png',
#    confianca=0.95
#)

DIRETORIO_IMAGENS = 'images'
caminhos_das_imagens = glob.glob(os.path.join(DIRETORIO_IMAGENS, '*.png'))

class AutoUltimatum:
    
    
    
    def __init__(self):
        DIRETORIO_IMAGENS = 'images'

        # Mods que arruinam a run. Nunca devem ser aceitos.
        self.bricks = [
            os.path.join(DIRETORIO_IMAGENS, 't10_brick.png'),
        ]

        # Whitelist do farm normal. Os bricks moram no mesmo diretorio,
        # entao precisam ser removidos daqui - senao o farm clicaria neles.
        todas = glob.glob(os.path.join(DIRETORIO_IMAGENS, '*.png'))
        bricks_norm = {os.path.normcase(os.path.abspath(b)) for b in self.bricks}
        self.caminhos_das_imagens = [
            p for p in todas
            if os.path.normcase(os.path.abspath(p)) not in bricks_norm
        ]

        self.retangulo = (1122, 604, 214, 110)

        self.take = os.path.join(DIRETORIO_IMAGENS, 'menus', 'TAKE.png')

        # Detector de "tela de escolha aberta" + botao de avancar rodada
        self.gatilho = os.path.join(DIRETORIO_IMAGENS, 'menus', 'base_or.png')
        self.regiao_gatilho = (863, 569, 200, 102)
        self.botao_continuar = (1234, 705)

        self.picks = {

        }
        self.modo = 'normal'  # 'normal' | 'grueling'
        self.rodando = threading.Event()
        self.encerrar = threading.Event()

    def brick_selecionado(self, confianca=.85):
        """
        True se o mod SELECIONADO pelo jogo for um brick.

        Usa comparacao em COR (cinza=False) de proposito: no grueling apenas a
        opcao auto-selecionada fica colorida, as outras ficam dessaturadas.
        Em preto e branco um brick nao-selecionado tambem daria match.
        """
        for caminho_brick in self.bricks:
            if encontrar(caminho_brick, confianca=confianca,
                         region=self.retangulo, cinza=False):
                print(f"BRICK selecionado: {caminho_brick}")
                return True
        return False

    def _ouvir_hotkeys(self):
        """Roda em thread separada monitorando as teclas de atalho."""
        toggle_antes = False
        sair_antes = False
        modo_antes = False

        while not self.encerrar.is_set():
            toggle_agora = tecla_pressionada(VK_TOGGLE)
            sair_agora = tecla_pressionada(VK_SAIR)
            modo_agora = tecla_pressionada(VK_MODO)

            # so reage na transicao solto -> pressionado
            if toggle_agora and not toggle_antes:
                if self.rodando.is_set():
                    self.rodando.clear()
                    print(">>> PAUSADO (F8 para retomar)")
                else:
                    self.rodando.set()
                    print(f">>> RODANDO em modo {self.modo.upper()} (F8 para pausar)")

            if modo_agora and not modo_antes:
                self.modo = 'grueling' if self.modo == 'normal' else 'normal'
                print(f">>> MODO: {self.modo.upper()}")

            if sair_agora and not sair_antes:
                print(">>> Encerrando...")
                self.encerrar.set()
                self.rodando.clear()

            toggle_antes = toggle_agora
            sair_antes = sair_agora
            modo_antes = modo_agora
            time.sleep(.03)

    def _continuar(self):
        """Clica no botao que avanca pra proxima rodada."""
        pyautogui.moveTo(*self.botao_continuar)
        time.sleep(.1)
        pyautogui.click()

    def _ciclo_normal(self):
        """Whitelist: procura um pick bom conhecido e clica nele."""
        if not encontrar(self.gatilho, confianca=.85, region=self.regiao_gatilho):
            return

        for i in self.caminhos_das_imagens:
            #print('---')
            if not self.rodando.is_set():
                break
            if not encontrar_e_clicar(i, region=self.retangulo):
                pass
            else:
                print(f"Encontrei {i}")
                break

        if self.rodando.is_set():
            self._continuar()

    def _ciclo_grueling(self):
        """
        Blacklist: o jogo ja escolheu o mod. Aceita qualquer coisa menos brick.
        Se veio brick, encerra a run clicando TAKE REWARD pra nao perder o loot.
        """
        if not encontrar(self.gatilho, confianca=.85, region=self.regiao_gatilho):
            return

        if self.brick_selecionado():
            # Nao da pra trocar o mod: a saida e sair com o que ja acumulou
            if encontrar_e_clicar(self.take, confianca=.85):
                print(">>> BRICK! Run encerrada com TAKE REWARD.")
            else:
                print(">>> BRICK detectado mas nao achei o TAKE REWARD na tela.")
            self.rodando.clear()
            print(">>> PAUSADO. Entre na proxima run e aperte F8.")
            return

        # Mod seguro - segue o jogo
        if self.rodando.is_set():
            self._continuar()

    def farm(self):
        threading.Thread(target=self._ouvir_hotkeys, daemon=True).start()
        print("F6 = sair | F7 = normal/grueling | F8 = iniciar/parar")
        print(f"Modo atual: {self.modo.upper()}")

        while not self.encerrar.is_set():
            if not self.rodando.is_set():
                time.sleep(.1)
                continue

            time.sleep(.2)

            if self.modo == 'grueling':
                self._ciclo_grueling()
            else:
                self._ciclo_normal()

ult = AutoUltimatum()
ult.farm()