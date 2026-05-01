# Handoff — Qwen3.6-35B-A3B Upgrade Research
> Fecha: 2026-05-01
> Estado: Pendiente de ejecución por el agente ingeniero
> Para: Claude Code / OpenCode / Gemini CLI (El Ingeniero)
> Fuente: Research manual del usuario + evidencia de Twitter/X

---

## Contexto

Durante una sesión de research se encontró evidencia concreta de que el modelo
Qwen3.6-35B-A3B puede correr en la RTX 3060 12GB con MoE offload a RAM,
alcanzando 40+ tok/s a 128k de contexto. Esto representaría una mejora significativa
sobre los modelos actuales del stack (Gemma 4 26B A4B Q4_K_M a ~40 tok/s con solo
8192 tokens de contexto).

---

## Evidencia recopilada

### Fuente: @above_spec en Twitter/X (30/04/2026, 92.8k visualizaciones)

**Benchmark principal — RTX 4060 Ti 8GB (MENOS VRAM que nuestra 3060):**

| Context Depth | Prompt Processing | Token Generation |
|---|---|---|
| 16,384 | 423.5 t/s | **41.55 t/s** |
| 50,000 | 402.1 t/s | 36.84 t/s |
| 100,000 | 369.5 t/s | 31.61 t/s |
| 150,000 | 343.9 t/s | 27.44 t/s |
| 200,000 | 332.2 t/s | 24.13 t/s |

**Setup del benchmark:**
- Hardware: Ryzen 9 7900X · 64 GB DDR5 · RTX 4060 Ti 8GB · Linux
- Runtime: llama.cpp build 11a241d
- Flags: -ngl 99 -ncmoe 99 -fa on -ctk q8_0 -ctv q8_0 -t 12 -tb 24
- Modelo: Qwen3.6-35B-A3B Q4_K_S · q8_0 KV cache · FlashAttention · MoE expert offload to CPU

**Por qué funciona (explicación técnica del autor):**
- Qwen3.6-35B activa solo 3B parámetros por token
- Atención + pesos compartidos se mantienen en GPU
- Expertos MoE fríos se pushean a RAM del sistema
- Con q8_0 KV cache + FlashAttention: 200k contexto cabe en ~2GB de VRAM
- Bottleneck real: bandwidth de RAM del host (~3B activos x Q4 = 1.5 GB/token de lecturas DDR)

### Evidencia directa para RTX 3060 12GB

Usuario @ItsmeAjayKV confirmó en el mismo hilo:
"I have a 3060 12GB. This is exactly my run configuration, MoE offload on
Qwen3.6-35B 5bit version, and got ~44t/s for 128k context."

Nuestra RTX 3060 tiene MÁS VRAM (12GB) que la 4060 Ti del benchmark (8GB).
La expectativa es igual o mejor performance que el benchmark publicado.

---

## Bloqueante identificado

La arquitectura del modelo es qwen3_5 (Gated DeltaNet) — una arquitectura nueva.
El build actual de llama.cpp en el servidor (compilado ~21 de abril 2026) puede
no tener soporte para esta arquitectura.

Acción requerida antes de descargar el modelo:
Verificar si el build actual soporta qwen3_5. Si no, recompilar llama.cpp.

---

## Plan de ejecución para el agente

### Fase 1 — Verificar build actual

```bash
~/llama.cpp/build/bin/llama-server --version
```

Anotar el build hash y comparar con 11a241d (build del benchmark).
Si el build es anterior o no reconoce qwen3_5, proceder a recompilar.

---

### Fase 2 — Actualizar llama.cpp

```bash
cd ~/llama.cpp
git pull origin master
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86
cmake --build build --config Release -j $(nproc)
```

Arquitectura CUDA 86 = Ampere (RTX 3060). No cambiar este valor.

Verificar que el nuevo build arranca:
```bash
~/llama.cpp/build/bin/llama-server --version
```

---

### Fase 3 — Buscar y descargar GGUF

El modelo base es Qwen/Qwen3.6-35B-A3B en Hugging Face.
Buscar cuantización Q4_K_M o Q4_K_S de terceros (bartowski o similar).

```bash
mkdir -p ~/models/qwen3
```

URLs a verificar:
- https://huggingface.co/bartowski/Qwen3.6-35B-A3B-GGUF
- https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF

Descargar Q4_K_M (~18GB estimado):
```bash
wget -c -O ~/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf \
  "[URL_DEL_GGUF_CONFIRMADO]"
```

---

### Fase 4 — Crear servicio systemd

```bash
sudo tee /etc/systemd/system/llama-qwen3.service > /dev/null << 'EOF'
[Unit]
Description=llama.cpp server - Qwen3.6-35B (codigo y razonamiento)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf \
  --alias qwen3-coder \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 131072 \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --jinja \
  --metrics \
  --slots \
  --slot-save-path /home/asalazar/llama-slots \
  --threads 6 \
  --threads-batch 24
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Diferencias vs servicios actuales:
- --ctx-size 131072 (128k) en lugar de 8192
- --n-cpu-moe 99 en lugar de 12
- --cache-type-k q8_0 --cache-type-v q8_0 (nuevo — reduce VRAM del KV cache)
- --threads-batch 24 en lugar de 6

---

### Fase 5 — Registrar en switch-model.sh

Agregar qwen3 como sexta opción al script ~/switch-model.sh:
- Agregar "qwen3" a la variable MODELS
- Agregar llama-qwen3 a la función stop_all_llm()
- Agregar caso en el bloque de modo LLM

Resultado esperado:
```bash
~/switch-model.sh qwen3     # codigo, razonamiento largo, 128k contexto
```

---

### Fase 6 — Validar

```bash
sudo systemctl daemon-reload
sudo systemctl enable llama-qwen3
~/switch-model.sh qwen3
curl -s http://localhost:8012/health | python3 -m json.tool
```

Test básico:
```bash
curl -s http://10.1.0.105:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder",
    "messages": [{"role": "user", "content": "Write a Python function to parse a GLTF file and extract all mesh names."}],
    "max_tokens": 500
  }' | python3 -m json.tool
```

Verificar en nvidia-smi que VRAM no excede 11GB durante inferencia.

---

## Impacto en el stack si se valida

| Capacidad | Hoy | Con Qwen3 |
|---|---|---|
| Contexto máximo | 8,192 tokens | 131,072 tokens (16x) |
| Velocidad | ~40 tok/s | ~40-44 tok/s |
| Rol | (nuevo) | Código y razonamiento técnico largo |
| Pipeline artista/ingeniero | Sin cambios | Sin cambios |

Qwen3.6-35B no reemplaza ningún modelo actual — se agrega como especialista
en código y contexto largo. Ornstein sigue siendo el modelo de briefs técnicos.
SuperGemma y TrevorJS siguen siendo los modelos creativos uncensored.

---

## Decisiones pendientes de formalizar (para context-save)

- D[XX]: Qwen3.6-35B-A3B identificado como viable para RTX 3060 12GB con
  MoE offload. Evidencia: benchmark público 4060 Ti 8GB + confirmación directa
  de usuario con 3060 12GB. Bloqueante: verificar soporte de arquitectura qwen3_5
  en build actual de llama.cpp antes de descargar.

- D[XX]: Preset validado de la comunidad para esta GPU:
  -ngl 99 -ncmoe 99 -fa on -ctk q8_0 -ctv q8_0 -t 12 -tb 24

- D[XX]: ctx-size objetivo 131072 (128k). KV cache q8_0 permite 200k en
  ~2GB de VRAM con FlashAttention activado.

---

## Notas para el agente

- Verificar build ANTES de descargar el modelo (18GB es mucho para descubrir
  que la arquitectura no está soportada)
- Si la recompilación falla, reportar el error exacto antes de continuar
- El preset usa --n-cpu-moe 99 (no 12 como los modelos actuales) — intencional
- No modificar los servicios de los modelos Gemma 4 existentes
- Si el modelo arranca pero da error de arquitectura desconocida, el build
  necesita actualización
