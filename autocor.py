import pyautogui
from pynput import mouse
import sys

# Função para converter uma tupla RGB em uma string HEX
def rgb_para_hex(rgb):
    """Converte uma tupla RGB (r, g, b) para uma string hexadecimal (#RRGGBB)."""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2]).upper()

def on_click(x, y, button, pressed):
    """Função chamada a cada evento de clique do mouse."""
    if pressed and button == mouse.Button.left:
        # Pega a cor RGB do pixel nas coordenadas (x, y)
        # pyautogui.pixel() retorna uma tupla (R, G, B)
        try:
            rgb_color = pyautogui.pixel(int(x), int(y))
            hex_color = rgb_para_hex(rgb_color)
            
            # Imprime os resultados no console
            print("--- Cor do Ponto Clicado ---")
            print(f"Coordenadas (X, Y): ({int(x)}, {int(y)})")
            print(f"Cor RGB: {rgb_color}")
            print(f"Cor HEX: {hex_color}")
            print("----------------------------\n")
            
            # Se você quiser parar o script após o primeiro clique, descomente a linha abaixo:
            # return False
            
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            # Se ocorrer um erro (por exemplo, permissão negada no Linux/macOS),
            # paramos o listener.
            return False

    # Condição para interromper o listener do mouse
    if pressed and button == mouse.Button.right:
        print("\nPrograma encerrado por clique com o botão direito.")
        return False # Isso encerra o listener do mouse

def iniciar_conta_gotas():
    print("Iniciando Conta-Gotas de Cores...")
    print("Clique com o **Botão Esquerdo** em qualquer lugar da tela para obter a cor.")
    print("Clique com o **Botão Direito** para encerrar o programa.")
    
    # Configura o listener do python 
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == '__main__':
    iniciar_conta_gotas()