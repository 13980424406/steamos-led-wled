<<<<<<< HEAD
# SteamOS LED → WLED

Replica a barra de LEDs do Steam Deck para um controlador [WLED](https://github.com/Aircoookie/WLED) via UDP DRGB, serial USB ou ambos. O modo serial USB envia quadros Adalight compatíveis com WLED diretamente para o WLED executado no ESP32-S3 conectado. Os 17 LEDs de origem são remapeados para o comprimento configurado da fita (1–256) com médias ponderadas; a saída é tratada como uma única fita linear, não como matriz.

Não é necessário firmware MCU personalizado. O ESP32-S3 executa WLED, que recebe os quadros pela serial USB e controla a saída de LEDs configurada.

**[English](README.md) | [简体中文](README.zh-CN.md)**
=======
# SteamOS LED → WLED Bridge

Replica a barra de LEDs do Steam Deck para um controlador [WLED](https://github.com/Aircoookie/WLED) via protocolo UDP realtime (DRGB).

Sem firmware customizado — basta um dispositivo WLED de fábrica na sua rede.

**[Read in English](README.md)**
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

## Como funciona

1. Lê snapshots de 100 bytes do `/dev/valve-leds-shim` (módulo kernel)
2. Remapeia 17 LEDs de origem para o comprimento da sua fita
3. Renderiza efeitos do Steam Deck no servidor (rainbow, breath, patrol, factory, demo)
4. Aplica overlays opcionais (temperatura, notificações, VU de áudio)
<<<<<<< HEAD
5. Envia pixels via **UDP DRGB** ao WLED e/ou **Adalight** pela serial USB
=======
5. Envia dados de pixel via **UDP DRGB** (porta 21324) para o WLED — mesmo protocolo do HyperHDR
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
6. Toca animações de boot/shutdown/suspend/resume

## Requisitos

- **Steam Deck** (SteamOS) ou PC Linux rodando Steam em Game Mode
<<<<<<< HEAD
- **Dispositivo WLED** na mesma rede quando usar a saída WLED
- **Controlador compatível com WLED** para saída serial USB; a Waveshare ESP32-S3-Matrix funciona com um build WLED que exponha serial USB
- **Python 3** (sem pacotes extras — usa apenas stdlib)

### Configurando o WLED

Para a saída UDP, configure um controlador WLED na rede antes de instalar esta bridge. A saída somente por serial USB não exige Wi-Fi nem endereço IP do WLED. Passos rápidos para a saída de rede:
=======
- **Dispositivo WLED** na mesma rede (ESP8266, ESP32, etc.)
- **Python 3** (sem pacotes extras — usa apenas stdlib)

### Configurando o WLED (pré-requisito)

Você precisa de um controlador WLED na sua rede antes de instalar esta bridge. Passos rápidos:
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

1. **Instale o WLED** em uma placa ESP8266 ou ESP32:
   - Baixe a última versão em [WLED releases](https://github.com/Aircoookie/WLED/releases)
   - Use o [instalador web WLED](https://install.wled.me/) (Chrome/Edge) para a forma mais fácil
2. **Conecte ao WiFi**: Após instalar, conecte ao hotspot `WLED-AP` e configure suas credenciais WiFi
3. **Configure a fita LED**: Em configurações do WLED → LED Preferences, defina a quantidade de LEDs e tipo (WS2812B, SK6812, etc.)
4. **Anote o endereço IP**: O WLED mostra o IP na página principal. O instalador também pode descobrir automaticamente
5. **Habilite sync UDP**: Em configurações do WLED → Sync Interfaces, certifique-se de que a porta UDP é **21324** (padrão)

Para instruções detalhadas, veja a [documentação do WLED](https://kno.wled.ge/).

## Instalação

```bash
git clone https://github.com/rpf16rj/steamos-led-wled.git
cd steamos-led-wled
sudo ./install.sh
```

O instalador vai:
<<<<<<< HEAD
1. Perguntar se deseja usar WLED, USB ou ambos
2. Descobrir dispositivos WLED automaticamente quando a saída WLED estiver ativa
3. Perguntar o dispositivo serial USB quando a saída USB estiver ativa
4. Perguntar a quantidade de LEDs lógicos e preferências de overlay
5. Compilar e instalar o módulo kernel `leds-valve-shim`
6. Instalar o serviço bridge e gerar `/etc/steamos-led-wled.conf`
7. Habilitar e iniciar o serviço systemd

### WLED na ESP32-S3-Matrix

Grave um build WLED compatível com a placa ESP32-S3 e que exponha sua interface serial USB. Em LED Preferences do WLED, configure o pino de dados dos LEDs integrados (GPIO 14 na Waveshare ESP32-S3-Matrix), o tipo e a quantidade de LEDs para corresponder a `num_leds`. A serial do WLED suporta Adalight; configure a taxa baud serial em Sync settings para corresponder a `usb_serial_baud` (padrão `115200`). A saída somente USB não exige Wi-Fi nem endereço IP do WLED.

O dispositivo no host geralmente é `/dev/ttyACM0`. Garanta que o usuário do serviço possa acessá-lo (normalmente pelo grupo `dialout` ou `uucp`). Consulte a [documentação serial do WLED](https://kno.wled.ge/interfaces/serial/) e a [referência da placa Waveshare](https://www.waveshare.com/wiki/ESP32-S3-Matrix).
=======
1. Tentar **descobrir automaticamente** dispositivos WLED na sua rede (mDNS / scan de subnet)
2. Caso não encontre, perguntar o IP manualmente
3. Perguntar quantidade de LEDs e preferências de overlay
4. Compilar e instalar o módulo kernel `leds-valve-shim`
5. Instalar o serviço bridge e gerar `/etc/steamos-led-wled.conf`
6. Habilitar e iniciar o serviço systemd
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

## Plugin Decky Loader

Controle os overlays diretamente do Game Mode usando o plugin Decky **Toolkit SteamOS Control**:

- Repositório: [toolkit-steamos-control-decky](https://github.com/rpf16rj/toolkit-steamos-control-decky)
- Ative/desative overlays de temperatura, VU de áudio e notificações sem sair do Game Mode

## Configuração

Edite `/etc/steamos-led-wled.conf`:

```ini
[steamos-led-wled]
<<<<<<< HEAD
# wled (UDP), usb (WLED Adalight via serial USB) ou both
output_mode = wled

=======
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
# Endereço IP do dispositivo WLED
wled_host = 192.168.1.100

# Porta UDP realtime do WLED (padrão: 21324)
wled_port = 21324

<<<<<<< HEAD
# Quantidade de LEDs lógicos enviados à saída (1-256)
num_leds = 8

# Dispositivo serial USB do WLED e baud rate
usb_serial_device = /dev/ttyACM0
usb_serial_baud = 115200

<<<<<<< HEAD
# Protocolo serial USB: adalight (padrão) ou json (WLED JSON over Serial)
usb_serial_protocol = adalight

=======
>>>>>>> 33c6e79ae49637ab7d5f2c271a536b28dfa341f1
=======
# Número de LEDs na sua fita (1-17)
num_leds = 8

>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
# Caminho para o dispositivo valve-leds-shim
device = /dev/valve-leds-shim

# Recursos de overlay (true/false)
temp_overlay = true
notify_overlay = true
audio_overlay = true
```

<<<<<<< HEAD
A origem contém 17 LEDs. `num_leds` pode variar de 1 a 256: saídas menores usam médias ponderadas para combinar LEDs de origem, enquanto saídas maiores distribuem os LEDs de origem pela fita usando médias ponderadas nas transições. Configure a fita WLED com a mesma quantidade de `num_leds`. Para saída somente USB, `wled_host` não é usado; defina `output_mode = usb`. Defina `output_mode = both` para espelhar cada quadro remapeado no WLED por UDP e pela serial USB.

<<<<<<< HEAD
Escolha o protocolo serial USB durante a instalação ou configure `usb_serial_protocol` manualmente: `adalight` (padrão, quadros binários Adalight) ou `json` (comandos JSON da API WLED delimitados por nova linha). Essa opção só é usada quando `output_mode` é `usb` ou `both`.

=======
>>>>>>> 33c6e79ae49637ab7d5f2c271a536b28dfa341f1
=======
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
Após editar, reinicie o serviço:

```bash
sudo systemctl restart steamos-led-wled
```

## Recursos

### Efeitos de LED (renderização no servidor)

<<<<<<< HEAD
Todos os efeitos de LED do Steam Deck são renderizados pela bridge e enviados às saídas configuradas:
=======
Todos os efeitos de LED do Steam Deck são renderizados pela bridge e enviados ao WLED:
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

| Efeito | Descrição |
|--------|-----------|
| **Manual** | Cor estática definida pelo Game Mode |
| **Rainbow** | Matizes ciclando por todos os LEDs |
| **Breath** | Brilho pulsante |
| **Patrol** | Luz ping-pong |
| **Factory** | Cores complementares alternadas |
| **Demo** | Cicla por todos os efeitos |

### Recursos de overlay

| Overlay | Descrição |
|---------|-----------|
| **Temperatura** | Colore a barra amarelo→vermelho baseado na temp CPU/GPU (> 65°C) |
| **Notificações** | Pisca dourado para conquistas, azul para mensagens |
| **VU de Áudio** | Medidor VU pelo áudio do sistema (PipeWire/PulseAudio) |

Prioridade: Notificação > Áudio+Temperatura > Game Mode

### Animações

| Evento | Animação |
|--------|----------|
| **Boot** | Sweep do centro para fora em azul Steam, depois pulso |
| **Shutdown** | Fade das bordas para o centro |
| **Suspend** | Fade lento para preto |
| **Resume** | Sweep rápido do centro para fora |

## Comandos

```bash
# Ver status
sudo systemctl status steamos-led-wled

# Ver logs
sudo journalctl -u steamos-led-wled -f

# Reiniciar
sudo systemctl restart steamos-led-wled

# Parar
sudo systemctl stop steamos-led-wled
```

## Desinstalar

```bash
sudo ./uninstall.sh
```

## Protocolo UDP

Usa o protocolo realtime **DRGB** do WLED na porta 21324:

| Byte | Valor | Descrição |
|------|-------|-----------|
| 0 | `0x02` | Protocolo: DRGB |
| 1 | `0x02` | Timeout: 2 segundos |
| 2+n×3 | R | Valor vermelho para LED n |
| 3+n×3 | G | Valor verde para LED n |
| 4+n×3 | B | Valor azul para LED n |

Este é o mesmo protocolo usado pelo HyperHDR, Hyperion e outras soluções ambilight.

<<<<<<< HEAD
## Protocolo serial USB

A saída USB envia quadros RGB completos usando o protocolo serial Adalight do WLED:

| Campo | Tamanho | Descrição |
|-------|---------|-----------|
| Cabeçalho | 3 bytes | ASCII `Ada` |
| Quantidade de pixels | 2 bytes | Quantidade menos um, big-endian |
| Checksum | 1 byte | Byte alto XOR byte baixo XOR `0x55` |
| Payload | 3 × quantidade | Bytes RGB na ordem física da cadeia (até 256 pelo host) |

Este é o protocolo serial documentado pelo WLED para dados de LED em tempo real. O protocolo MCU personalizado anterior `SLW1` não é mais enviado; use WLED no ESP32-S3 em vez de compilar o firmware MCU separado.

=======
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
## Licença

MIT
