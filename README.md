# FGBind-Net inference package

This folder contains a minimal inference package for FGBind-Net, a
foreground-background guided sequence-level model for protein-ligand binding
affinity prediction.

## Recommended public files

For a minimal GitHub release, include:

- `predict_torchscript.py`: command-line inference script.
- `fgbind_net_inference.pt`: TorchScript inference model.
- `example_input.csv`: a small example input file.
- `example_predictions.csv`: expected output for the example input.
- `README.md`: this usage guide.
- `requirements.txt`: Python dependencies.

The full training scripts, Python model source, experimental notebooks, raw
PDBbind data and internal analysis files are not included in this minimal
inference package.

## Input format

`predict_torchscript.py` expects a CSV file with the following columns:

```text
pdb_id,ligand_smiles,full_protein_seq,fg_pocket_seq,bg_protein_seq
```

Column meanings:

- `pdb_id`: complex identifier.
- `ligand_smiles`: ligand SMILES string.
- `full_protein_seq`: full protein sequence.
- `fg_pocket_seq`: pocket residue sequence used as foreground input.
- `bg_protein_seq`: non-pocket protein sequence used as background input.

The original PDBbind data are not redistributed here. Users should obtain
PDBbind from the official database subject to its terms of use.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run prediction:

```bash
python predict_torchscript.py \
  --input example_input.csv \
  --model fgbind_net_inference.pt \
  --output predictions.csv
```

Use CPU explicitly:

```bash
python predict_torchscript.py \
  --input example_input.csv \
  --model fgbind_net_inference.pt \
  --output predictions.csv \
  --device cpu
```

The output CSV contains:

```text
pdb_id,predicted_affinity
```

## Sequence lengths and tokenization

The released checkpoint uses the following maximum lengths:

- background protein sequence: 819
- foreground pocket sequence: 66
- ligand SMILES: 153

Longer inputs are truncated and shorter inputs are padded with the mask token.
Unknown characters are mapped to the mask token.

## Suggested citation

If you use this model, please cite the associated manuscript:

FGBind-Net: foreground-background guided local-global modeling for
protein-ligand binding affinity prediction.
