# MLOps Batch Signal Pipeline

This project implements a minimal MLOps-style batch pipeline for generating trading signals from OHLCV data.
The system is designed to demonstrate core production engineering principles: reproducibility via configuration and seed control, observability through structured logging and metrics, and deployment readiness using Docker.

The pipeline reads a dataset of market prices, computes a rolling mean over the `close` column, and generates a binary signal indicating whether the current price is above the rolling average. It outputs both aggregated metrics (`metrics.json`) and detailed execution logs (`run.log`). Additionally, a row-level dataset (`signals.csv`) is produced for inspection and downstream use.

---

## 📦 Project Structure

```
.
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json      # sample output
├── run.log           # sample log
├── signals.csv       # generated signal output
```

---

## ⬇️ Clone the Repository

```bash
git clone https://github.com/mathml-ai/mlops_task/

```

---

## 🔄 Pull Latest Changes

```bash
git pull origin main
```

---

## ⚙️ Running Locally (without Docker)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline

```bash
python run.py \
  --input data.csv \
  --config config.yaml \
  --output metrics.json \
  --log-file run.log
```

### 3. Outputs generated

* `metrics.json` → summary metrics
* `run.log` → execution logs
* `signals.csv` → row-level signal data

---

## 🐳 Running with Docker

### 1. Build the image

```bash
docker build -t mlops-task .
```

### 2. Run the container

```bash
docker run --rm mlops-task
```

### 3. Outputs

The container will:

* Print final metrics JSON to stdout
* Generate:

  * `metrics.json`
  * `run.log`
  * `signals.csv`

---

## 📊 Example Output (`metrics.json`)

```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 73,
  "seed": 42,
  "status": "success"
}
```

---

## 🧠 Notes

* The pipeline is deterministic (controlled by seed and config)
* Handles malformed CSV inputs (e.g., single-column parsing issues)
* Logs all major steps for observability
* Ensures metrics are written in both success and failure cases
