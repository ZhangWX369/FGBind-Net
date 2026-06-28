# FGBind-Net

FGBind-Net is a foreground-background guided sequence-level model for
protein-ligand binding affinity prediction. It uses ligand SMILES, pocket
sequence and non-pocket protein sequence information to estimate binding
affinity.

This repository provides resources for running FGBind-Net predictions, including
the released inference model, a prediction script, and example input/output
files.

## Files

```text
fgbind_net_inference.pt     Released FGBind-Net inference model
predict_torchscript.py      Prediction script
example_input.csv           Example input file
example_predictions.csv     Example output file
requirements.txt            Python dependencies
README.md                   Usage instructions
```

## Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The prediction script uses PyTorch, NumPy and pandas.

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

## Input format

The input file should be a CSV table with the following columns:

```text
pdb_id,ligand_smiles,full_protein_seq,fg_pocket_seq,bg_protein_seq
```

Column descriptions:

- `pdb_id`: complex identifier.
- `ligand_smiles`: ligand SMILES string.
- `full_protein_seq`: full protein sequence.
- `fg_pocket_seq`: binding-pocket sequence used as foreground input.
- `bg_protein_seq`: non-pocket protein sequence used as background input.

The original PDBbind data should be obtained from the PDBbind database according
to its terms of use.

## Prediction

Run prediction with the provided example file:

```bash
python predict_torchscript.py \
  --input example_input.csv \
  --model fgbind_net_inference.pt \
  --output predictions.csv
```

To run on CPU:

```bash
python predict_torchscript.py \
  --input example_input.csv \
  --model fgbind_net_inference.pt \
  --output predictions.csv \
  --device cpu
```

The output file contains:

```text
pdb_id,predicted_affinity
```

## Model input lengths

The released inference model uses the following maximum lengths:

- background protein sequence: 819
- foreground pocket sequence: 66
- ligand SMILES: 153

Longer inputs are truncated to the maximum length. Shorter inputs are padded
with the mask token. Characters outside the predefined vocabulary are mapped to
the mask token.

## Example

The repository includes `example_input.csv` and the corresponding
`example_predictions.csv` for a quick format check.

## Citation

If you use FGBind-Net, please cite:

FGBind-Net: foreground-background guided local-global modeling for
protein-ligand binding affinity prediction.
