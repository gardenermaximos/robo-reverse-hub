# RCJ Reverse-Engineering & Prototyping Hub

Hub de Engenharia Reversa e Prototipagem para **RoboCupJunior Soccer (Infrared)**.

**Fluxo:** Foto de robô → calibração de escala → detecção estrutural 2.5D → **CadPlan (JSON)** → (a) lista de comandos na UI + (b) modelagem 3D automática no Fusion 360 via Add-in.

---

## Como subir o backend

```bash
cd backend
uv sync          # cria venv e instala dependências
uv run uvicorn app.main:app --reload --port 8000
```

Acesse: http://127.0.0.1:8000/api/health

---

## Como instalar o Add-in no Fusion 360

1. Abra o Fusion 360 com um design vazio ativo.
2. `UTILITIES` → **Scripts and Add-Ins** (`Shift+S`) → aba **Add-Ins**.
3. Botão **`+`** → *Add existing…* → selecionar a pasta `fusion_addin/RCJBridge`.
4. Selecionar **RCJBridge** → **Run**.
5. Ver mensagens em *Text Commands* (`Ctrl+Alt+C`).

Verificar que o Add-in está rodando:

```bash
curl -s -H "X-RCJ-Token: troque-este-token" http://127.0.0.1:8765/health
```

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```
GEMINI_API_KEY=<sua chave>
GEMINI_MODEL=<modelo multimodal vigente>
FUSION_TOKEN=<mesmo token do config.json do Add-in>
```

---

## Documentação

- `ARCHITECTURE.md` — fonte de verdade de arquitetura, contratos JSON, API
- `HANDOFF.md` — estado atual, checklist por etapa
- `docs/decisions.md` — decisões de implementação
- `docs/fusion-api-notes.md` — armadilhas da API do Fusion 360
