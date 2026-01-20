import os
import pandas as pd
import numpy as np


def run_topsis(input_file, weights_str, impacts_str, output_file):
    # --------------------------------------------------
    # 1. Check if input file exists
    # --------------------------------------------------
    if not os.path.isfile(input_file):
        raise ValueError("Input file not found.")

    # --------------------------------------------------
    # 2. Read input file (CSV or XLSX)
    # --------------------------------------------------
    try:
        if input_file.endswith(".csv"):
            data = pd.read_csv(input_file)
        elif input_file.endswith(".xlsx"):
            data = pd.read_excel(input_file)
        else:
            raise ValueError("Input file must be a .csv or .xlsx file.")
    except Exception as e:
        raise ValueError(f"Unable to read input file: {e}")

    # --------------------------------------------------
    # 3. Minimum column check (>= 3 columns)
    # --------------------------------------------------
    if data.shape[1] < 3:
        raise ValueError("Input file must contain at least three columns.")

    # --------------------------------------------------
    # 4. Extract criteria columns (2nd to last)
    # --------------------------------------------------
    criteria = data.iloc[:, 1:]

    # --------------------------------------------------
    # 5. Numeric validation
    # --------------------------------------------------
    try:
        criteria = criteria.apply(pd.to_numeric)
    except ValueError:
        raise ValueError("From 2nd to last columns must contain numeric values only.")

    # --------------------------------------------------
    # 6. Validate weights (comma-separated & numeric)
    # --------------------------------------------------
    try:
        weights = [float(w.strip()) for w in weights_str.split(",")]
        if len(weights) < 2:
            raise ValueError
    except:
        raise ValueError("Weights must be numeric and separated by commas.")

    # --------------------------------------------------
    # 7. Validate impacts (comma-separated & + / -)
    # --------------------------------------------------
    impacts = [i.strip() for i in impacts_str.split(",")]

    if len(impacts) < 2 or any(i not in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be either '+' or '-' and separated by commas.")

    # --------------------------------------------------
    # 8. Check counts match
    # --------------------------------------------------
    if len(weights) != criteria.shape[1] or len(impacts) != criteria.shape[1]:
        raise ValueError(
            "Number of weights, impacts, and criteria columns must be the same."
        )

    # --------------------------------------------------
    # ---------------- TOPSIS STEPS --------------------
    # --------------------------------------------------

    # Step 1: Normalize
    norm = np.sqrt((criteria ** 2).sum())
    normalized = criteria / norm

    # Step 2: Apply weights
    weighted = normalized * weights

    # Step 3: Ideal best & worst
    ideal_best = []
    ideal_worst = []

    for i in range(len(impacts)):
        if impacts[i] == '+':
            ideal_best.append(weighted.iloc[:, i].max())
            ideal_worst.append(weighted.iloc[:, i].min())
        else:
            ideal_best.append(weighted.iloc[:, i].min())
            ideal_worst.append(weighted.iloc[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    # Step 4: Distance measures
    dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    # Step 5: Topsis score
    topsis_score = dist_worst / (dist_best + dist_worst)

    # Step 6: Ranking
    rank = topsis_score.rank(ascending=False, method='dense').astype(int)

    # --------------------------------------------------
    # 9. Prepare output
    # --------------------------------------------------
    result = data.copy()
    result["Topsis Score"] = topsis_score.round(4)
    result["Rank"] = rank

    # --------------------------------------------------
    # 10. Save output file
    # --------------------------------------------------
    try:
        result.to_csv(output_file, index=False)
    except Exception as e:
        raise ValueError(f"Unable to write output file: {e}")

    return output_file
