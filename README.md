# Twisted Collatz Manifold (TCM)

**Parameterized Collatz Dynamics: Phase Transitions, Hausdorff Dimension, and Arithmetic Fractal Families**

> Preliminary research communication. All results independently verified.

---

## Overview

This repository contains the simulation code and figure generation scripts for the paper:

> *"Parameterized Collatz Dynamics: Phase Transitions, Hausdorff Dimension, and Arithmetic Fractal Families in Twisted Collatz Systems"*

We introduce two parameterized extensions of the Collatz iteration controlled by a time-varying twist factor `tau(k) = tau_0 * delta^k`:

| Variant | Domain | Floor? | Key property |
|---------|--------|--------|--------------|
| **TCM-Integer** | n ∈ Z+ | Yes | Always converges (δ < 1) |
| **TCM-Continuous** | n ∈ R+ | No | Strange cycles, phase transition |

---

## Key Results

- **Proposition 3.1**: All TCM-Integer trajectories reach 1 for any δ < 1
- **Lemma 3.1**: Lyapunov function decreases by > 1 + log₂(n) at every even step
- **Phase transition**: Strange cycle count peaks at ~93 attractors near δ ≈ 0.986
- **Hausdorff dimension**: D_H ∈ [1.46, 1.83] for fractal family F(δ), peak near δ ≈ 0.995
- **Two distinct peaks**: Attractor diversity (δ = 0.986) and fractal complexity (δ = 0.995)

---

## Repository Structure

```
tcm-collatz/
├── README.md
├── requirements.txt
├── tcm_final.py          # Core TCM implementations (Integer + Continuous)
├── hausdorff.py          # Box-counting Hausdorff dimension computation
├── figures/
│   ├── figure1_phase_transition.png
│   ├── figure2_strange_cycles.png
│   ├── figure3_fractal.png
│   ├── figure4_lyapunov.png
│   └── figure5_hausdorff.png
└── paper/
    └── TCM_Paper_v3_2.pdf
```

---

## Installation

```bash
git clone https://github.com/[username]/tcm-collatz
cd tcm-collatz
pip install -r requirements.txt
```

**Requirements**: Python 3.8+, numpy, scipy, matplotlib

---

## Usage

### Run full verification and generate all figures

```bash
python tcm_final.py
```

This will:
- Verify Proposition 3.1 (convergence) for δ ∈ {0.5, 0.9, 0.99, 0.999, 0.9999}
- Verify Lemma 3.1 (Lyapunov) for all even n ≤ 100,000
- Verify Θ^(0)(27) = −296.51 with 3-step manual check
- Generate Figures 1–4

### Compute Hausdorff dimensions

```bash
python hausdorff.py
```

This will:
- Compute D_H for δ ∈ {0.980, 0.985, 0.990, 0.995, 0.999}
- Generate Figure 5 with log-log plots and D_H vs δ
- Save numerical results to `hausdorff_results.npy`

**Note**: Hausdorff computation takes approximately 5–10 minutes on a standard laptop.

---

## Core API

### TCM-Integer

```python
from tcm_final import tcm_integer

# Run trajectory from n=27, delta=0.9999
steps, converged, max_val = tcm_integer(27, delta=0.9999)
print(f"Steps: {steps}, Converged: {converged}, Max: {max_val}")
```

### TCM-Continuous

```python
from tcm_final import tcm_continuous

# Check for strange cycles at delta=0.986
attr_type, attr_val, steps = tcm_continuous(27, delta=0.986)
print(f"Type: {attr_type}, Attractor: {attr_val}")
```

### Lyapunov Trajectory

```python
from tcm_final import lyapunov_trajectory_integer

# Compute verified Lyapunov values for n=27
records = lyapunov_trajectory_integer(27)
# records: list of (step, n, is_odd, theta_k, Theta_cum, V)
print(f"Theta final: {records[-1][4]:.3f}")  # -296.514
```

---

## Development Note

This framework was developed with AI assistance (Claude, Anthropic).
Numerical results were verified by separate Python implementation
(this repository). Reader verification is encouraged — all code
is provided for this purpose.

AI assistance was used for: framework development, code writing,
paper drafting, and numerical checking. The mathematical ideas,
corrections, and final judgment on all claims are the author's.

---

## Verified Numerical Results

All claims verified by Python implementation in this repository:

| Claim | Value | Verified |
|-------|-------|----------|
| Θ^(0)(27) | −296.51 | ✓ |
| Step 0 theta (n=27) | +5.086 | ✓ |
| Step 1 theta (n=27) | −6.358 | ✓ |
| Step 2 theta (n=27) | +5.563 | ✓ |
| Peak strange cycles | ~93 at δ=0.986 | ✓ |
| Peak D_H | 1.825 at δ=0.995 | ✓ |
| Lemma 3.1 violations | 0 for n ≤ 100,000 | ✓ |

---

## Correction Notice

Version 1.0 of this framework reported Θ^(0)(27) ≈ −18.92.
This was a computation error (undocumented scale factor in early prototype).
The correct value is **−296.51**, verified independently.
The error has been retracted and documented in all paper versions.

---

## Citation

If you use this code or build on these results, please cite:

```
@misc{pham2026tcm,
  author = {Pham Tien Manh},
  title  = {Parameterized Collatz Dynamics: Phase Transitions,
             Hausdorff Dimension, and Arithmetic Fractal Families
             in Twisted Collatz Systems},
  year   = {2026},
  note   = {Preliminary research communication. arXiv preprint.}
}
```

*(arXiv ID will be added after submission)*

---

## License

MIT License. See LICENSE file.

---

## Author

**Pham Tien Manh** (Phạm Tiến Mạnh)
Independent Researcher

Feedback, questions, and collaboration welcome.
Please open a GitHub issue or contact via arXiv.
