# SVNFSR-MCDM Online Demo

An online demonstration of the Reliability-aware Single-Valued Neutrosophic Fuzzy Soft Relation (SVNFSR) model for Multi-Criteria Decision Making.

## Features

- Upload Excel input
- Criterion weight calculation
- Reliability-aware normalization
- Relation matrix construction
- Dominance analysis
- Final ranking
- Export results

## Run locally

```bash
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py

```

## Input format

Matrix sheet

```
Alternative | C1 | C2 | ...
S1          | (T,I,F)/μ
```

Criteria sheet

```
Criterion | E | C
```

## Citation

If you use this code, please cite our paper.