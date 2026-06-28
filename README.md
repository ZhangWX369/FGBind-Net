# FGBind-Net

FGBind-Net is a foreground-background guided sequence-level model for
protein-ligand binding affinity prediction. It uses ligand SMILES, pocket
sequence and non-pocket protein sequence information to estimate binding
affinity.

This repository provides the released FGBind-Net inference model, processed
benchmark data tables, and an evaluation script for reproducing the reported
CASF-2013 and CASF-2016 test results.

## Files

```text
fgbind_net_inference.pt     Released FGBind-Net inference model
evaluate_fgbind.py          Prediction and evaluation script
requirements.txt            Python dependencies
README.md                   Usage instructions

data/train.csv              Training set feature table
data/validation.csv         Validation set feature table
data/casf2013.csv           CASF-2013 test set feature table
data/casf2016.csv           CASF-2016 test set feature table
```

## Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Tested environment

The prediction workflow was tested under the following environment:

```text
Operating system: Ubuntu 22.04.1 LTS, Linux kernel 6.8.0-85-generic
Python: 3.10.8
PyTorch: 2.6.0+cu124
CUDA: 12.4
cuDNN: 9.1.0
NumPy: 1.26.4
pandas: 1.4.2
SciPy: 1.15.3
scikit-learn: 1.7.2
matplotlib: 3.4.3
tqdm: 4.67.3
RDKit: 2024.3.2
GPU: NVIDIA GeForce RTX 4070 Ti
NVIDIA driver: 535.171.04
```

## Data format

Each CSV file in `data/` contains the following columns:

```text
pdb_id,affinity,full_protein_seq,fg_pocket_seq,bg_protein_seq,ligand_smiles
```

Column descriptions:

- `pdb_id`: complex identifier.
- `affinity`: experimental binding affinity value.
- `full_protein_seq`: full protein sequence.
- `fg_pocket_seq`: binding-pocket sequence used as foreground input.
- `bg_protein_seq`: non-pocket protein sequence used as background input.
- `ligand_smiles`: ligand SMILES string.

The processed feature tables were generated from PDBbind v2020 and the CASF
benchmark sets. Original PDBbind resources should be cited and used according
to their terms of use.

## Reproducing benchmark metrics

Run evaluation on CASF-2013 and CASF-2016:

```bash
python evaluate_fgbind.py \
  --model fgbind_net_inference.pt \
  --input data/casf2013.csv data/casf2016.csv \
  --output-dir results
```

The script writes prediction files and a metric summary:

```text
results/casf2013_predictions.csv
results/casf2016_predictions.csv
results/metrics_summary.csv
```

The summary contains five metrics: RMSE, PCC, MAE, SD and CI.

Expected benchmark results:

```text
Dataset     RMSE    PCC     MAE     SD      CI
CASF-2016   1.171   0.846   0.917   1.158   0.829
CASF-2013   1.384   0.792   1.120   1.374   0.793
```

To evaluate additional feature tables, pass them after `--input`:

```bash
python evaluate_fgbind.py \
  --model fgbind_net_inference.pt \
  --input data/validation.csv \
  --output-dir results_validation
```

## Model input lengths

The released inference model uses the following maximum lengths:

- background protein sequence: 819
- foreground pocket sequence: 66
- ligand SMILES: 153

Longer inputs are truncated to the maximum length. Shorter inputs are padded
with the mask token. Characters outside the predefined vocabulary are mapped to
the mask token.

## Citation

If you use FGBind-Net, please cite:

FGBind-Net: foreground-background guided local-global modeling for
protein-ligand binding affinity prediction.
