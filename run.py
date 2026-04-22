import argparse
import yaml
import pandas as pd
import numpy as np
import logging
import json
import time
import sys
import os


def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_config(path):
    if not os.path.exists(path):
        raise ValueError("Config file not found")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    required = ["seed", "window", "version"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    return config


def load_data(path):
    if not os.path.exists(path):
        raise ValueError("Input file not found")

    try:
        df = pd.read_csv(path)
    except Exception:
        raise ValueError("Invalid CSV format")

    if df.empty:
        raise ValueError("Empty dataset")

    # 🧠 Case: everything parsed into one column
    if len(df.columns) == 1:
        logging.warning("Detected single-column CSV. Attempting recovery...")

        raw = df.iloc[:, 0].astype(str)

        # Split all rows
        split_df = raw.str.split(",", expand=True)

        # 🚨 Detect if first row is header
        first_row = split_df.iloc[0].tolist()

        expected_cols = ["timestamp", "open", "high", "low", "close"]

        if all(col in first_row for col in expected_cols):
            # ✅ Proper header exists
            split_df.columns = first_row
            df = split_df[1:].reset_index(drop=True)
            logging.info("Header detected and applied from first row")
        else:
            # ❗ No header → assign manually
            df = split_df.copy()
            df.columns = [
                "timestamp", "open", "high", "low",
                "close", "volume_btc", "volume_usd"
            ]
            logging.info("No header found, assigned default column names")

    # ✅ Validate required column
    if "close" not in df.columns:
        raise ValueError("Missing 'close' column")

    # 🔢 Convert numeric safely
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if df["close"].isna().all():
        raise ValueError("'close' column invalid or non-numeric")

    logging.info(f"Final columns: {list(df.columns)}")

    return df

def compute_signal(df, window):
    # Rolling mean
    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    # Drop NaNs once → this is your final working dataset
    df_processed = df.dropna().copy()

    # Compute signal
    df_processed["signal"] = (
        df_processed["close"] > df_processed["rolling_mean"]
    ).astype(int)

    # 📈 Save signals as side artifact
    signals_path = "signals.csv"

    cols = [c for c in ["timestamp", "close", "rolling_mean", "signal"] if c in df_processed.columns]
    df_processed[cols].to_csv(signals_path, index=False)

    logging.info(f"Signals file written: {signals_path}")
    logging.info(f"Processed rows (after rolling): {len(df_processed)}")

    # ✅ Return the SAME processed dataframe
    return df_processed


def write_metrics(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    setup_logger(args.log_file)
    start_time = time.time()

    try:
        logging.info("Job started")

        # Config
        config = load_config(args.config)
        logging.info(f"Config loaded: {config}")

        np.random.seed(config["seed"])

        # Data
        df = load_data(args.input)
        logging.info(f"Rows loaded: {len(df)}")

        # Processing
        df = compute_signal(df, config["window"])
        logging.info("Rolling mean + signal computed")

        rows_processed = len(df)
        signal_rate = df["signal"].mean()

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        logging.info(f"Metrics: {metrics}")
        logging.info("Job completed successfully")

        write_metrics(args.output, metrics)

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        logging.error(f"Error: {str(e)}")
        logging.info("Job failed")

        write_metrics(args.output, error_metrics)

        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()