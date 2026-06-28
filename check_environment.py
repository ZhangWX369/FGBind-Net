import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime


REQUIRED_PACKAGES = [
    ("torch", "torch"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
]

OPTIONAL_PACKAGES = [
    ("scipy", "scipy"),
    ("sklearn", "scikit-learn"),
    ("matplotlib", "matplotlib"),
    ("tqdm", "tqdm"),
    ("rdkit", "rdkit"),
    ("Bio", "biopython"),
]


def package_version(distribution_name):
    try:
        return importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def import_status(module_name):
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except Exception as exc:
        return {"available": False, "error": str(exc)}

    return {
        "available": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def collect_torch_info():
    info = {
        "installed": False,
        "version": package_version("torch"),
        "cuda_compiled": None,
        "cuda_available": None,
        "cudnn_version": None,
        "gpu_count": 0,
        "gpus": [],
    }
    try:
        import torch
    except Exception as exc:
        info["import_error"] = str(exc)
        return info

    info["installed"] = True
    info["version"] = torch.__version__
    info["cuda_compiled"] = torch.version.cuda
    info["cuda_available"] = torch.cuda.is_available()
    info["cudnn_version"] = torch.backends.cudnn.version()
    info["gpu_count"] = torch.cuda.device_count()
    for index in range(info["gpu_count"]):
        props = torch.cuda.get_device_properties(index)
        info["gpus"].append(
            {
                "index": index,
                "name": torch.cuda.get_device_name(index),
                "total_memory_gb": round(props.total_memory / 1024**3, 2),
                "compute_capability": f"{props.major}.{props.minor}",
            }
        )
    return info


def collect_environment():
    packages = {}
    for module_name, distribution_name in REQUIRED_PACKAGES + OPTIONAL_PACKAGES:
        packages[distribution_name] = {
            "module": module_name,
            "version": package_version(distribution_name),
            "importable": import_status(module_name),
        }

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "python": {
            "version": sys.version.replace("\n", " "),
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "packages": packages,
        "torch": collect_torch_info(),
        "nvidia_smi": run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ]
        ),
    }


def print_report(env):
    print("FGBind-Net environment report")
    print("=" * 32)
    print(f"Generated at: {env['generated_at']}")
    print(f"Python: {env['python']['version']}")
    print(f"Python executable: {env['python']['executable']}")
    print(
        "Platform: "
        f"{env['platform']['system']} {env['platform']['release']} "
        f"({env['platform']['machine']})"
    )
    print()

    print("Required packages")
    print("-" * 17)
    for _, distribution_name in REQUIRED_PACKAGES:
        item = env["packages"][distribution_name]
        print(
            f"{distribution_name:14s} "
            f"version={item['version'] or 'not installed':18s} "
            f"importable={item['importable']}"
        )
    print()

    print("Optional packages")
    print("-" * 17)
    for _, distribution_name in OPTIONAL_PACKAGES:
        item = env["packages"][distribution_name]
        print(
            f"{distribution_name:14s} "
            f"version={item['version'] or 'not installed':18s} "
            f"importable={item['importable']}"
        )
    print()

    torch_info = env["torch"]
    print("PyTorch / GPU")
    print("-" * 13)
    print(f"torch version: {torch_info.get('version') or 'not installed'}")
    print(f"CUDA compiled: {torch_info.get('cuda_compiled')}")
    print(f"CUDA available: {torch_info.get('cuda_available')}")
    print(f"cuDNN version: {torch_info.get('cudnn_version')}")
    print(f"GPU count: {torch_info.get('gpu_count')}")
    for gpu in torch_info.get("gpus", []):
        print(
            f"GPU {gpu['index']}: {gpu['name']} "
            f"({gpu['total_memory_gb']} GB, compute {gpu['compute_capability']})"
        )
    if "import_error" in torch_info:
        print(f"torch import error: {torch_info['import_error']}")
    print()

    print("nvidia-smi")
    print("-" * 10)
    nvidia = env["nvidia_smi"]
    if nvidia["available"]:
        print(nvidia["stdout"])
    else:
        print("not available")
        if nvidia.get("stderr"):
            print(nvidia["stderr"])
        if nvidia.get("error"):
            print(nvidia["error"])


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print the Python/package/GPU environment used for FGBind-Net."
    )
    parser.add_argument(
        "--output",
        default="environment_info.json",
        help="Optional JSON output path. Default: environment_info.json.",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Do not write the JSON environment report.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    env = collect_environment()
    print_report(env)
    if not args.no_json:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(env, handle, indent=2, ensure_ascii=False)
        print()
        print(f"Saved JSON report to: {args.output}")


if __name__ == "__main__":
    main()
