# SWE-agent Setup Guide

Quick setup guide for running SWE-agent on Ubuntu 22.04.

---

## 1. Install Python 3.11

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

---

## 2. Install Docker

```bash
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo chmod 666 /var/run/docker.sock
```

Test Docker works:
```bash
docker ps
```

---

## 3. Install SWE-agent

```bash
cd ~
git clone https://github.com/princeton-nlp/SWE-agent.git
cd SWE-agent
python3.11 -m pip install --upgrade pip
python3.11 -m pip install --editable .
python3.11 -m pip install swebench sb-cli
```

---

## 4. Configure API Keys

Create `.env` file in `SWE-agent/` directory:

```env
AZURE_OPENAI_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
SWEBENCH_API_KEY="your-swebench-key"
```

---

## 5. Run SWE-agent

```bash
cd ~/SWE-agent
sweagent run-batch \
  --config config/swe_prompt.yaml \
  --num_workers 5 \
  --instances.type swe_bench \
  --instances.subset lite \
  --instances.split dev \
  --instances.evaluate True \
  --instances.slice :3 \
  --instances.shuffle True
```

Results saved in: `trajectories/`

---

## Troubleshooting

**Docker permission error:**
```bash
sudo chmod 666 /var/run/docker.sock
```

**Command not found:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```
