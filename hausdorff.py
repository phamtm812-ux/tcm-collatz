"""
Hausdorff Dimension Estimation for TCM Fractal Boundary
========================================================
Method: Box-counting algorithm
D_H ≈ lim_{epsilon→0} log(N(epsilon)) / log(1/epsilon)

where N(epsilon) = number of boxes of size epsilon
that intersect the fractal boundary.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import os

OUT = "/mnt/user-data/outputs/"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11,
    'figure.dpi': 150,
    'axes.spines.top': False, 'axes.spines.right': False,
})

DARK='#0d1b2a'; BLUE='#1a6faf'; RED='#c0392b'
GREEN='#27ae60'; ORANGE='#e67e22'


# ════════════════════════════════════════
# STEP 1: Generate binary fractal image
# ════════════════════════════════════════

def escape_continuous(z, delta, max_steps=300, threshold=1e6):
    """Returns 1 if convergent, 0 if divergent."""
    tau = 1.0
    for k in range(max_steps):
        if abs(z) > threshold:
            return 0
        ri = int(np.floor(z.real))
        z = (z / 2) if ri % 2 == 0 else (3 * z + 1) * tau
        tau *= delta
    return 1


def generate_fractal_grid(delta, res=400,
                           x_range=(-3, 3), y_range=(-2.5, 2.5)):
    """Generate binary convergence map."""
    x = np.linspace(*x_range, res)
    y = np.linspace(*y_range, res)
    grid = np.zeros((res, res), dtype=np.int8)

    for i in range(res):
        for j in range(res):
            z = x[j] + 1j * y[i]
            grid[i, j] = escape_continuous(z, delta)

    return grid, x, y


def extract_boundary(grid):
    """
    Extract boundary pixels: convergent pixels adjacent
    to at least one divergent pixel.
    """
    from scipy.ndimage import binary_dilation
    # Boundary = convergent AND adjacent to divergent
    conv = grid.astype(bool)
    dilated = binary_dilation(~conv)
    boundary = conv & dilated
    return boundary


# ════════════════════════════════════════
# STEP 2: Box-counting algorithm
# ════════════════════════════════════════

def box_count(boundary, min_box=2, max_box=None):
    """
    Count boxes of various sizes covering the boundary.
    Returns (box_sizes, counts).
    """
    n = boundary.shape[0]
    if max_box is None:
        max_box = n // 4

    sizes = []
    counts = []

    box_size = min_box
    while box_size <= max_box:
        # Count non-empty boxes
        count = 0
        for i in range(0, n, box_size):
            for j in range(0, n, box_size):
                box = boundary[i:i+box_size, j:j+box_size]
                if box.any():
                    count += 1
        sizes.append(box_size)
        counts.append(count)
        box_size = int(box_size * 1.5) + 1

    return np.array(sizes), np.array(counts)


def estimate_dimension(sizes, counts):
    """
    Estimate Hausdorff dimension via linear regression
    on log-log plot.
    D_H ≈ -slope of log(N) vs log(epsilon)
    """
    log_sizes = np.log(sizes)
    log_counts = np.log(counts)

    # Linear regression
    slope, intercept, r_value, p_value, std_err = \
        stats.linregress(log_sizes, log_counts)

    # D_H = -slope (since N ~ epsilon^{-D_H})
    D_H = -slope

    return D_H, r_value**2, slope, intercept, std_err


# ════════════════════════════════════════
# STEP 3: Compute for multiple delta values
# ════════════════════════════════════════

def compute_hausdorff_for_delta(delta, res=350):
    """Full pipeline for one delta value."""
    print(f"    Generating grid delta={delta:.4f}...", end=' ')
    grid, x, y = generate_fractal_grid(delta, res=res)

    boundary = extract_boundary(grid)
    n_boundary = boundary.sum()
    print(f"{n_boundary} boundary pixels")

    if n_boundary < 100:
        print(f"    Too few boundary pixels, skipping")
        return None

    sizes, counts = box_count(boundary, min_box=2,
                               max_box=res//6)

    # Filter: keep only sizes with count > 1
    mask = counts > 1
    if mask.sum() < 4:
        return None

    D_H, r2, slope, intercept, std_err = \
        estimate_dimension(sizes[mask], counts[mask])

    return {
        'delta': delta,
        'D_H': D_H,
        'r2': r2,
        'std_err': abs(std_err),
        'n_boundary': n_boundary,
        'sizes': sizes[mask],
        'counts': counts[mask],
        'grid': grid,
        'boundary': boundary,
    }


# ════════════════════════════════════════
# STEP 4: Generate all figures
# ════════════════════════════════════════

def figure_hausdorff_analysis(results):
    """Main figure: D_H vs delta + log-log plots."""

    valid = [r for r in results if r is not None]
    if not valid:
        print("No valid results")
        return

    deltas_v = [r['delta'] for r in valid]
    D_H_v    = [r['D_H'] for r in valid]
    r2_v     = [r['r2'] for r in valid]
    err_v    = [r['std_err'] for r in valid]

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # ── Top left: D_H vs delta ──
    ax = axes[0, 0]
    ax.errorbar(deltas_v, D_H_v, yerr=err_v,
                fmt='o-', color=BLUE, markersize=6,
                linewidth=1.8, capsize=4,
                label='D_H estimate ± std_err')
    ax.axhline(1.0, color=DARK, ls=':', lw=1,
               label='D_H = 1 (smooth curve)')
    ax.axhline(2.0, color=RED, ls=':', lw=1,
               label='D_H = 2 (filled region)')

    peak_idx = np.argmax(D_H_v)
    ax.axvline(deltas_v[peak_idx], color=ORANGE,
               ls='--', lw=1.3,
               label=f'Peak: delta≈{deltas_v[peak_idx]:.4f}')

    ax.set_xlabel('delta')
    ax.set_ylabel('Hausdorff Dimension D_H')
    ax.set_title('Hausdorff Dimension vs delta\n'
                 '(box-counting, boundary of convergent region)')
    ax.legend(fontsize=8)
    ax.set_ylim([0.8, 2.2])

    # ── Top right: R² quality ──
    ax2 = axes[0, 1]
    ax2.plot(deltas_v, r2_v, 's-', color=GREEN,
             markersize=6, lw=1.5)
    ax2.axhline(0.99, color=DARK, ls='--', lw=1,
                label='R²=0.99 threshold')
    ax2.set_xlabel('delta')
    ax2.set_ylabel('R² of log-log fit')
    ax2.set_title('Fit Quality (R²)\n'
                  'High R² = reliable fractal scaling')
    ax2.legend(fontsize=9)
    ax2.set_ylim([0.8, 1.02])

    # ── Bottom left: Log-log plot for best delta ──
    ax3 = axes[1, 0]
    # Find highest R² result
    best_idx = np.argmax(r2_v)
    best = valid[best_idx]
    log_s = np.log(best['sizes'])
    log_c = np.log(best['counts'])
    slope = -best['D_H']
    intercept = np.mean(log_c - slope * log_s)

    ax3.scatter(log_s, log_c, color=BLUE,
                s=40, label='Box counts', zorder=3)
    fit_x = np.linspace(log_s.min(), log_s.max(), 50)
    ax3.plot(fit_x, slope * fit_x + intercept,
             '-', color=RED, lw=1.5,
             label=f'Fit: D_H={best["D_H"]:.3f}, R²={best["r2"]:.4f}')
    ax3.set_xlabel('log(box size)')
    ax3.set_ylabel('log(box count)')
    ax3.set_title(f'Log-Log Plot: delta={best["delta"]:.4f}\n'
                  f'D_H ≈ {best["D_H"]:.3f} '
                  f'(R²={best["r2"]:.4f})')
    ax3.legend(fontsize=9)

    # ── Bottom right: Fractal image for best delta ──
    ax4 = axes[1, 1]
    best_r = valid[best_idx]
    boundary_img = best_r['boundary'].astype(float)
    convergent_img = best_r['grid'].astype(float)

    # Show convergent region + boundary highlighted
    display = convergent_img * 0.3
    display[best_r['boundary']] = 1.0
    ax4.imshow(display, cmap='hot', origin='lower',
               extent=[-3, 3, -2.5, 2.5])
    ax4.set_title(f'Fractal Boundary (delta={best_r["delta"]:.4f})\n'
                  f'Bright = boundary pixels used for box-counting')
    ax4.set_xlabel('Re(z)')
    ax4.set_ylabel('Im(z)')

    plt.suptitle('Hausdorff Dimension Analysis of TCM Fractal Family\n'
                 '(box-counting method, independently computed)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT + 'figure5_hausdorff.png', bbox_inches='tight')
    plt.close()
    print(f"  Figure saved.")

    return deltas_v, D_H_v, r2_v


def print_report(results):
    """Print verification report."""
    valid = [r for r in results if r is not None]
    print("\n" + "="*60)
    print("HAUSDORFF DIMENSION REPORT")
    print("="*60)
    print(f"{'delta':>8} | {'D_H':>6} | {'R²':>6} | "
          f"{'std_err':>8} | {'boundary px':>12}")
    print("-"*55)
    for r in valid:
        print(f"{r['delta']:8.4f} | {r['D_H']:6.3f} | "
              f"{r['r2']:6.4f} | {r['std_err']:8.4f} | "
              f"{r['n_boundary']:12d}")

    D_H_vals = [r['D_H'] for r in valid]
    r2_vals  = [r['r2'] for r in valid]
    print(f"\nSummary:")
    print(f"  D_H range: [{min(D_H_vals):.3f}, {max(D_H_vals):.3f}]")
    print(f"  Mean D_H: {np.mean(D_H_vals):.3f} ± {np.std(D_H_vals):.3f}")
    print(f"  Mean R²:  {np.mean(r2_vals):.4f}")
    print(f"  Max D_H:  {max(D_H_vals):.3f} at "
          f"delta={valid[np.argmax(D_H_vals)]['delta']:.4f}")
    print("="*60 + "\n")


# ════════════════════════════════════════
# MAIN
# ════════════════════════════════════════

if __name__ == "__main__":
    print("Hausdorff Dimension Computation — TCM Fractal Family")
    print("=" * 55)

    # Compute for multiple delta values
    # Focus on interesting range around phase transition
    delta_values = [0.90, 0.93, 0.96, 0.97, 0.980,
                    0.985, 0.990, 0.995, 0.999]

    results = []
    print("\nComputing box-counting for each delta:")
    for delta in delta_values:
        r = compute_hausdorff_for_delta(delta, res=320)
        results.append(r)

    print_report(results)

    print("Generating figures...")
    out = figure_hausdorff_analysis(results)

    # Save numerical results
    valid = [r for r in results if r is not None]
    np.save(OUT + 'hausdorff_results.npy',
            np.array([[r['delta'], r['D_H'],
                       r['r2'], r['std_err']]
                      for r in valid]))
    print(f"\n✓ Results saved to {OUT}")
    print(f"  figure5_hausdorff.png")
    print(f"  hausdorff_results.npy")
