from vpython import *
import numpy as np

running = False

# Pausa ou inicia a simulação
def toggle_run(b):
    global running
    running = not running
    b.text = "Pause" if running else "Play"

# Reseta a simulação
def reset_sim(b):
    global r_particula, v_particula, velocidade, particula, trajetoria, tempo, B_vetor, q, m, V_ajustado, B_ajustado, label_b, label_v
    
    try:
        new_Bx = float(BX_input.text)
        new_By = float(BY_input.text)
        new_Bz = float(BZ_input.text)
        new_q = 1.602e-19 # falta permitir o usuário modificar a carga
        new_m = 1.672e-27 # falta permitir o usuário modificar a massa
        new_vx = float(VX_input.text)
        new_vy = float(VY_input.text)
        new_vz = float(VZ_input.text)
    except ValueError:
        print("Erro: Verifique se todos os campos de entrada contêm números válidos.")
        return
        
    q = new_q
    m = new_m

    # Novo vetor do campo magnético enviado pelo usuário
    B_vetor = vector(new_Bx, new_By, new_Bz)
    
    # reseta a posição original da particula
    r_particula = vector(0, 0, 0)

    # Novo vetor velocidade enviado pelo usuário
    v_particula = vector(new_vx, new_vy, new_vz)

    # Escalonar vetores (velocidade)
    V_unitario = hat(v_particula)
    V_ajustado = V_unitario * 0.05

    # Escalonar vetores (campo magnético)
    B_unitario = hat(B_vetor)
    B_ajustado = B_unitario * 0.05

    particula.pos = r_particula
    velocidade.pos = r_particula
    campo_b.pos = r_particula - B_ajustado/2
    trajetoria.clear()
    trajetoria.append(pos=r_particula)
    tempo = 0
    campo_b.axis = B_ajustado
    velocidade.axis = V_ajustado
    label_b.pos = campo_b.pos + campo_b.axis
    label_v.pos = velocidade.pos + velocidade.axis

# ----------------- 1. CONFIGURAÇÃO DA CENA -----------------
scene.title = "Trajetória de Partícula em Campo Magnético Uniforme"
scene.width = 800
scene.height = 600
scene.autoscale = True
scene.range = 0.05 # Define o zoom inicial da cena

scene.append_to_caption('\n\n') # Adiciona quebra de linha

# Criação dos CAMPOS DE ENTRADA (winput)
scene.append_to_caption('<h3>**Parâmetros da Simulação:**</h3>\n')
scene.append_to_caption('Campo B (T): ')
scene.append_to_caption('X:')
BX_input = winput(bind=reset_sim, text='0')
scene.append_to_caption(' Y:')
BY_input = winput(bind=reset_sim, text='0')
scene.append_to_caption(' Z:')
BZ_input = winput(bind=reset_sim, text='0.5')
scene.append_to_caption('\nCarga 1 (C): ')
Q_input = winput(bind=reset_sim, text='1.602e-19')
scene.append_to_caption('\nMassa m (kg): ')
M_input = winput(bind=reset_sim, text='1.672e-27')
scene.append_to_caption('\nVelocidade inicial V (m/s): ')
scene.append_to_caption('X:')
VX_input = winput(bind=reset_sim, text='1e6')
scene.append_to_caption(' Y:')
VY_input = winput(bind=reset_sim, text='0')
scene.append_to_caption(' Z:')
VZ_input = winput(bind=reset_sim, text='0')
scene.append_to_caption('\n\n')

# ----------------- 2. CONSTANTES E OBJETOS GRÁFICOS -----------------
# Constantes Físicas (as mesmas de antes)
q = 1.602e-19  # Carga (C)
m = 1.672e-27  # Massa (kg)
Bz_mag = 0.5   # Magnitude do campo (T)
Vx = 1e6       # Velocidade (m/s)
dt = 1e-9      # Passo de tempo (s)

# Definição do vetor B e Vetor de Posição Inicial
B_vetor = vector(0, 0, Bz_mag) # Vetor VPython
r_inicial = vector(0, 0, 0) # posição inicial da particula
v_inicial = vector(Vx, 0, 0) # Velocidade 

# Variáveis mutáveis
r_particula = r_inicial
v_particula = v_inicial

button(text="Play", bind=toggle_run)
scene.append_to_caption('   ')
button(text="Reset", bind=reset_sim)

# Escalonar vetores (velocidade)
V_unitario = hat(v_particula)
V_ajustado = V_unitario * 0.05

# Escalonar vetores (campo magnético)
B_unitario = hat(B_vetor)
B_ajustado = B_unitario * 0.05

# Partícula (Esfera)
raio_esfera = 0.005
particula = sphere(pos=r_particula, radius=raio_esfera, color=color.red, make_trail=False)

# Campo Magnético (Seta)
campo_b = arrow(pos=vector(0, 0, 0) - B_vetor * 0.1/2, axis=B_ajustado, color=color.red, shaftwidth=raio_esfera/4)
label_b = label(pos=campo_b.pos + campo_b.axis, text='B', color=color.red, xoffset=20, yoffset=10)

# Velocidade (Seta)
velocidade = arrow(pos=r_particula, axis=V_ajustado, color=color.blue, shaftwidth=raio_esfera/4)
label_v = label(pos=velocidade.pos + velocidade.axis, text='V', color=color.blue, xoffset=20, yoffset=10)

# Trajetória (Curva)
trajetoria = curve(color=color.red, radius=raio_esfera/10)


# ----------------- 3. LOOP DE SIMULAÇÃO E ANIMAÇÃO -----------------
tempo = 0
N_frames = 0

while True:
    # 1000 iterações por segundo.
    rate(100)
    if running:
        # Passo 1: Calcular a Aceleração ATUAL (a_i)
        produto_vetorial_i = cross(v_particula, B_vetor)
        F_i = q * produto_vetorial_i
        a_i = F_i / m

        # Passo 2: Calcular a Velocidade de TESTE (v_trial) - Método de Euler simples
        v_trial = v_particula + a_i * dt

        # Passo 3: Calcular a Aceleração de TESTE (a_trial)
        produto_vetorial_trial = cross(v_trial, B_vetor)
        F_trial = q * produto_vetorial_trial
        a_trial = F_trial / m

        # Passo 4: Atualizar a Velocidade (v_i+1) - Usando a média das acelerações
        a_media = 0.5 * (a_i + a_trial)
        v_particula = v_particula + a_media * dt

        # Passo 5: Atualizar a Posição (r_i+1) - Usando a média das velocidades
        # Aqui, para o Euler Melhorado ser mais estável, podemos usar a média de v_i e v_i+1
        # Uma forma comum é: r_particula = r_particula + v_particula * dt
        # Mas vamos usar o valor mais atualizado da velocidade:
        r_particula = r_particula + v_particula * dt # Variação do Euler Melhorado

        # 6. Atualizar a visualização 3D
        particula.pos = r_particula
        velocidade.pos = r_particula
        V_unitario = hat(v_particula)
        V_ajustado = V_unitario * 0.05
        velocidade.axis = V_ajustado
        label_v.pos = velocidade.pos + velocidade.axis
        trajetoria.append(pos=r_particula)

        # Avança no tempo
        tempo += dt
        N_frames += 1