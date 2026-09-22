import pyautogui
import time
import random
import glob
import os
import ctypes
import threading
from ctypes import wintypes, windll, byref

from pyautogui import ImageNotFoundException

# Hotkeys globais (Windows) - codigos de virtual-key
VK_SAIR = 0x75    # F6  -> encerra o script
VK_MODO = 0x76    # F7  -> alterna normal <-> grueling
VK_TOGGLE = 0x77  # F8  -> inicia/para

_user32 = ctypes.windll.user32

# Posição fixa para o mouse no final da interação
POSICAO_ESC_X = 3500
POSICAO_ESC_Y = 750

PAUSA_ESC = .05

# Flag para controlar se o mouse está bloqueado
MOUSE_BLOQUEADO = False
# Flag para armazenar se o mouse estava em hold no início da interação
ESTAVA_EM_HOLD = False
# Lock para sincronização
LOCK_BLOQUEIO = threading.Lock()

# Definições para BlockInput
def bloquear_entradas(bloquear):
    """
    Bloqueia ou desbloqueia todas as entradas de mouse e teclado.
    bloquear = True -> bloqueia
    bloquear = False -> desbloqueia
    Retorna True se funcionou, False se falhou.
    """
    try:
        # Importa a função BlockInput do user32.dll
        BlockInput = _user32.BlockInput
        BlockInput.restype = ctypes.c_bool
        result = BlockInput(ctypes.c_bool(bloquear))
        return bool(result)
    except Exception as e:
        print(f"Erro ao chamar BlockInput: {e}")
        return False

def tecla_pressionada(vk_code):
    """True se a tecla estiver pressionada agora, mesmo sem foco na janela."""
    return bool(_user32.GetAsyncKeyState(vk_code) & 0x8000)

def mouse_em_hold():
    """
    Verifica se o botão esquerdo do mouse está pressionado (hold).
    Retorna True se estiver pressionado, False caso contrário.
    """
    return bool(_user32.GetAsyncKeyState(0x01) & 0x8000)  # 0x01 = VK_LBUTTON

def preparar_interacao():
    """
    Se o mouse estiver em hold (botão esquerdo pressionado):
    1. Salva o estado de hold
    2. BLOQUEIA TODAS AS ENTRADAS (mouse e teclado) - NÃO TEM COMO MOVER!
    3. Solta o botão esquerdo do mouse
    4. Pressiona ESC
    """
    global ESTAVA_EM_HOLD, MOUSE_BLOQUEADO
    
    # Verifica se o mouse está em hold e salva o estado
    ESTAVA_EM_HOLD = mouse_em_hold()
    
    if not ESTAVA_EM_HOLD:
        return
    
    # --- BLOQUEIA TODAS AS ENTRADAS ---
    # Isso impede QUALQUER movimento do mouse
    with LOCK_BLOQUEIO:
        if bloquear_entradas(True):
            MOUSE_BLOQUEADO = True
            print(">>> Entradas BLOQUEADAS (mouse e teclado) - BlockInput ativo")
        else:
            print(">>> FALHA ao bloquear entradas! Verifique permissões de administrador.")
            return
    
    time.sleep(0.05)
    
    # Pega a posição atual do mouse (já que o usuário não pode mover)
    pos_atual = pyautogui.position()
    print(f">>> Posição atual do mouse: ({pos_atual.x}, {pos_atual.y})")
    
    # 2. Solta o botão esquerdo do mouse
    pyautogui.mouseUp(button='left')
    time.sleep(0.02)
    
    # 3. Pressiona ESC
    pyautogui.press('esc')
    time.sleep(PAUSA_ESC)

def finalizar_interacao():
    """
    Se o mouse estava em hold no início, executa no FINAL de cada interação:
    1. Move o mouse para (3500, 750)
    2. Clica (sem segurar)
    3. Pressiona ESC
    4. DESBLOQUEIA TODAS AS ENTRADAS
    5. Se estava em hold, pressiona o botão esquerdo novamente (left button down)
    """
    global ESTAVA_EM_HOLD, MOUSE_BLOQUEADO
    
    if not ESTAVA_EM_HOLD:
        return

    print(">>> Executando ações finais do ESC...")
    
    # DESBLOQUEIA as entradas ANTES de mover o mouse
    # (senão o script também não consegue mover)
    with LOCK_BLOQUEIO:
        if MOUSE_BLOQUEADO:
            if bloquear_entradas(False):
                MOUSE_BLOQUEADO = False
                print(">>> Entradas DESBLOQUEADAS")
            else:
                print(">>> FALHA ao desbloquear entradas!")
                # Tenta novamente
                bloquear_entradas(False)
                MOUSE_BLOQUEADO = False
            time.sleep(0.05)
    
    # 1. Move para a posição fixa
    pyautogui.moveTo(POSICAO_ESC_X, POSICAO_ESC_Y, duration=0.1)
    time.sleep(0.05)
    
    # 2. Clica (clique simples, sem segurar)
    pyautogui.click()
    time.sleep(0.02)
    
    # 3. Pressiona ESC
    pyautogui.press('esc')
    time.sleep(PAUSA_ESC)
    
    # 4. Se estava em hold, pressiona o botão esquerdo novamente
    if ESTAVA_EM_HOLD:
        pyautogui.mouseDown(button='left')
        print(">>> Left button DOWN (restaurando hold)")
        time.sleep(0.02)
    
    # Reseta a flag
    ESTAVA_EM_HOLD = False

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
        return False
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return False

def encontrar_e_clicar(nome_arquivo_imagem, confianca=0.85, region=None, cinza=True):
    """
    Tenta encontrar uma imagem na tela e clicar em um ponto aleatório dentro dela.
    """
    try:
        # Retorna o retângulo (left, top, width, height) da imagem
        regiao = pyautogui.locateOnScreen(nome_arquivo_imagem, confidence=confianca, region=region, grayscale=cinza)

        if regiao:
            x, y, largura, altura = regiao
            
            # --- INÍCIO DA INTERAÇÃO ---
            # 1. Verifica hold, BLOQUEIA entradas (mouse e teclado)
            preparar_interacao()

            # 2. Move para o alvo (com entradas bloqueadas, só o script pode mover)
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(.05)
            
            # 3. Clica no alvo
            pyautogui.click(x, y)
            
            # --- FIM DA INTERAÇÃO ---
            # 4. Move para (3500, 750), clica, pressiona ESC, DESBLOQUEIA e restaura hold
            finalizar_interacao()
            
            return True
        else:
            print(f"Não foi possível encontrar a imagem '{nome_arquivo_imagem}' na tela.")
            return False

    except ImageNotFoundException:
        return False
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return False

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
            toggle_agora = tecla_pressionada(0x77)  # F8
            sair_agora = tecla_pressionada(0x75)    # F6
            modo_agora = tecla_pressionada(0x76)    # F7

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
        # --- INÍCIO DA INTERAÇÃO ---
        preparar_interacao()
        
        # Move e clica no botão continuar (entradas bloqueadas)
        pyautogui.moveTo(*self.botao_continuar, duration=0.1)
        time.sleep(.05)
        pyautogui.click()
        
        # --- FIM DA INTERAÇÃO ---
        finalizar_interacao()

    def _ciclo_normal(self):
        """Whitelist: procura um pick bom conhecido e clica nele."""
        if not encontrar(self.gatilho, confianca=.85, region=self.regiao_gatilho):
            return

        for i in self.caminhos_das_imagens:
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
        print(">>> MODO ESC: AUTOMÁTICO (detecta hold do mouse)")
        print(">>> BLOQUEIO: BlockInput (bloqueia mouse E teclado)")

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