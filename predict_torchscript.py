import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset


SMI_CHAR_SET = {
    "<MASK>": 0, "C": 1, ")": 2, "(": 3, "c": 4, "O": 5, "]": 6, "[": 7,
    "@": 8, "1": 9, "=": 10, "H": 11, "N": 12, "2": 13, "n": 14,
    "3": 15, "o": 16, "+": 17, "-": 18, "S": 19, "F": 20, "p": 21,
    "l": 22, "/": 23, "4": 24, "#": 25, "B": 26, "\\": 27, "5": 28,
    "r": 29, "s": 30, "6": 31, "I": 32, "7": 33, "%": 34, "8": 35,
    "e": 36, "P": 37, "9": 38, "R": 39, "u": 40, "0": 41, "i": 42,
    ".": 43, "A": 44, "t": 45, "h": 46, "V": 47, "g": 48, "b": 49,
    "Z": 50, "T": 51, "M": 52,
}

SEQ_CHAR_SET = {
    "<MASK>": 0, "A": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6,
    "H": 7, "K": 8, "I": 9, "L": 10, "M": 11, "N": 12, "P": 13,
    "Q": 14, "R": 15, "S": 16, "T": 17, "V": 18, "Y": 19, "W": 20,
}

PROTEIN_SEQ_LEN = 819
POCKET_SEQ_LEN = 66
SMI_LEN = 153


def encode_text(value, vocab, max_len):
    encoded = np.zeros(max_len, dtype=np.int64)
    if not isinstance(value, str):
        return encoded
    for i, token in enumerate(value[:max_len]):
        encoded[i] = vocab.get(token, 0)
    return encoded


class FGBindInferenceDataset(Dataset):
    required_columns = [
        "pdb_id",
        "ligand_smiles",
        "full_protein_seq",
        "fg_pocket_seq",
        "bg_protein_seq",
    ]

    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        missing = [col for col in self.required_columns if col not in self.data.columns]
        if missing:
            raise ValueError("Input CSV is missing required columns: " + ", ".join(missing))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        pdb_id = str(row["pdb_id"])
        smi = torch.tensor(encode_text(row["ligand_smiles"], SMI_CHAR_SET, SMI_LEN)).long()
        bg_seq = torch.tensor(
            encode_text(row["bg_protein_seq"], SEQ_CHAR_SET, PROTEIN_SEQ_LEN)
        ).long()
        pocket_seq = torch.tensor(
            encode_text(row["fg_pocket_seq"], SEQ_CHAR_SET, POCKET_SEQ_LEN)
        ).long()
        mask_pocket = torch.zeros(PROTEIN_SEQ_LEN, dtype=torch.long)
        return pdb_id, pocket_seq, smi, bg_seq, mask_pocket


def resolve_device(device_arg):
    if device_arg == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_arg)


def predict(args):
    device = resolve_device(args.device)
    dataset = FGBindInferenceDataset(args.input)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False)
    model = torch.jit.load(args.model, map_location=device)
    model.eval()

    records = []
    with torch.no_grad():
        for pdb_ids, pocket_seq, smi, bg_seq, mask_pocket in loader:
            pocket_seq = pocket_seq.to(device)
            smi = smi.to(device)
            bg_seq = bg_seq.to(device)
            mask_pocket = mask_pocket.to(device)
            y_hat = model(pocket_seq, smi, bg_seq, smi, mask_pocket)
            predictions = y_hat.detach().cpu().numpy().reshape(-1)
            for pdb_id, pred in zip(pdb_ids, predictions):
                records.append({"pdb_id": pdb_id, "predicted_affinity": float(pred)})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(output_path, index=False)
    print(f"Saved {len(records)} predictions to {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run FGBind-Net prediction with a TorchScript inference model."
    )
    parser.add_argument("--input", required=True, help="Input feature CSV.")
    parser.add_argument(
        "--model",
        default="fgbind_net_inference.pt",
        help="TorchScript model path. Default: fgbind_net_inference.pt.",
    )
    parser.add_argument(
        "--output",
        default="fgbind_predictions.csv",
        help="Output CSV path. Default: fgbind_predictions.csv.",
    )
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--device", default="auto", help="auto, cpu, cuda, or cuda:0.")
    return parser.parse_args()


if __name__ == "__main__":
    predict(parse_args())
