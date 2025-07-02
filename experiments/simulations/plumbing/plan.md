# Hybrid Multi‑Fidelity Dataset Plan for Residential Plumbing **Leak Prognosis** (Detection & Time‑to‑Leak Prediction)

## Table of Contents

1. [Overview](#overview)
2. [Objectives](#objectives)
3. [Toolchain Components](#toolchain-components)

   1. [Low‑Fidelity: EPANET / WNTR](#low-fidelity)
   2. [High‑Fidelity: SimScale CFD](#high-fidelity)
4. [End‑to‑End Workflow](#workflow)

   1. [Step 1 – Build the Low‑Fidelity Corpus](#step1)
   2. [Step 2 – Generate High‑Fidelity Anchors](#step2)
   3. [Step 3 – Align the Two Fidelities](#step3)
   4. [Step 4 – Train with Knowledge Distillation](#step4)
   5. [Step 5 – Validate & Iterate](#step5)
5. [Data & Folder Structure](#structure)
6. [Compute & Cost Guardrails](#cost)
7. [Key References](#references)

---

## <a name="overview"></a>1. Overview

This plan combines **thousands of quick, hydraulically‑reasonable EPANET/WNTR simulations** with **tens to hundreds of high‑fidelity SimScale CFD runs**.  A corrective model (Δ‑model) and a teacher–student knowledge‑distillation step close the physics gap, giving you a wide corpus that still carries realistic leak signatures.

```
   EPANET/WNTR (10 000+ scenarios)  ──►  Δ‑model  ──►  ML Student
          ▲                                   ▲
          │                                   │
   SimScale CFD (~100 anchors)  ──────────────┘
```

---

## <a name="objectives"></a>2. Objectives

* **Breadth:** Cover leak sizes, start times, demand profiles, pipe materials, supply pressures, *and healthy periods* for baseline learning.
* **Depth:** Capture sub‑second transients (pressure waves, cavitation) that EPANET cannot model.
* **Predictive power:** Train models that output calibrated probabilities of a leak occurring within multiple future horizons (24 h, 72 h, 14 days).
* **Actionability:** Provide interpretable drivers (e.g., sustained high night‑time flow, rising pressure variance) so maintenance teams know *why* risk is rising.
* **Scalability:** Keep compute cost under control while producing 10 k+ labelled traces augmented with time‑to‑event labels.
* **ML‑readiness:** Output unified CSV/Parquet files with sensor‑centric columns, leak labels, and time‑to‑leak targets.

---

## <a name="toolchain-components"></a>3. Toolchain Components

### <a name="low-fidelity"></a>3.1 Low‑Fidelity: EPANET / WNTR

| Feature                         | Why it matters                              |
| ------------------------------- | ------------------------------------------- |
| Fast extended‑period hydraulics | Run 24‑h, 1‑s simulations in ≪1 min.        |
| Python API (WNTR)               | Script Monte‑Carlo sweeps & leak insertion. |
| Node/pipe attributes            | Store metadata: material, diameter, age.    |

### <a name="high-fidelity"></a>3.2 High‑Fidelity: SimScale CFD

| Feature                                       | Why it matters                                        |
| --------------------------------------------- | ----------------------------------------------------- |
| Transient incompressible / multiphase solvers | Resolve leak jets & pressure waves.                   |
| Point probes & result controls                | Export time‑series identical to virtual sensors.      |
| Parametric studies & Python SDK               | Automate sweeps across leak area, material, pressure. |

**Note:** All simulations use a single sensor placed just downstream of the main house shutoff valve, capturing both pressure and flow measurements at this critical system entry point.

---

## <a name="workflow"></a>4. End‑to‑End Workflow

### <a name="step1"></a>4.1 Step 1 – Build the Low‑Fidelity Corpus

1. **Residential skeleton**: ½‑inch PEX/Cu branches; PRV at entry; fixture demands.
2. **Leak injection** (WNTR):

   ```python
   wntr.scenario.leak_horizontal_pipe(
       pipe_name="KitchenRun",
       start_time=3*3600,           # seconds
       leak_area=math.pi*(0.003**2),  # 3 mm hole
       duration=1800               # 30 min
   )
   ```
3. **Monte‑Carlo sweep**: vary leak\_area (0.5–10 mm), supply\_pressure (275–550 kPa), demand profile seeds, pipe material, leak location.
4. **Export** 1‑s pressure & flow CSVs per scenario.

### <a name="step2"></a>4.2 Step 2 – Generate High‑Fidelity Anchors

1. **Select anchor cases**: 5 pipes × 3 materials × 3 leak sizes ≈ 45 runs.
2. **CAD & mesh once** per pipe type; reuse mesh for all parameter studies.
3. **Transient CFD**: Δt = 0.001–0.01 s, T = 30 s.
4. **Point probe** just downstream of the main house shutoff valve; export CSV via Python SDK.

### <a name="step3"></a>4.3 Step 3 – Align the Two Fidelities

1. **Temporal resampling**: SimScale → 1 s; or EPANET → 100 ms.
2. **Spatial mapping**: probe\_id ↔ node\_id lookup.
3. **Δ‑model**: learn `Δ = HighFid − LowFid` with Gaussian‑Process or small CNN using anchor pairs.
4. **Augment** every EPANET trace: `P_corr = P_low + Δ̂`.

### <a name="step4"></a>4.4 Step 4 – Train with Knowledge Distillation & Time‑to‑Leak Prediction

1. **Teacher** (small LSTM) trains only on anchors for both *leak classification* **and** *time‑to‑event (survival) regression* (e.g., Weibull likelihood head).
2. **Student** (1‑D CNN + Transformer) trains on the full corrected corpus with a multi‑task loss combining classification cross‑entropy, distillation KL‑divergence, and survival negative log‑likelihood.
3. Calibrate the survival head with isotonic regression so that statements like “20 % chance of leak within 3 days” are well‑calibrated.
4. Early‑stop on held‑out CFD traces and concordance index for time‑to‑leak prediction.

### <a name="step5"></a>4.5 Step 5 – Validate & Iterate

| Metric                           | Target           |
| -------------------------------- | ---------------- |
| Metric                           | Target           |
| --------                         | --------         |
| Pressure RMSE (CFD vs corrected) | ≤ 5 kPa          |
| Leak detection F1                | ≥ 0.95           |
| Localization error               | ≤ 1 pipe segment |
| Time‑to‑leak C‑index             | ≥ 0.80           |
| 72 h leak‑risk Brier score       | ≤ 0.15           |

---

## <a name="structure"></a>5. Data & Folder Structure

```
/dataset/
    epanet_raw/
        run_00001.csv
        ...
    epanet_corrected/
        run_00001_corr.csv
    simscale_anchors/
        case_cu_3mm_probe.csv
    metadata/
        scenarios.json          # parameters per run
        mapping_probes.json     # CFD ↔ EPANET node map
/models/
    teacher.pt
    student.pt
/notebooks/
    01_epanet_sweep.ipynb
    02_simscale_api.ipynb
    03_delta_model.ipynb
```

---

## <a name="cost"></a>6. Compute & Cost Guardrails

| Component                                     | Estimate                        |
| --------------------------------------------- | ------------------------------- |
| **EPANET/WNTR sweep** (10 k runs @ 30 s each) |  < 6 CPU‑hours (laptop)         |
| **SimScale anchors** (45 runs × 2 core‑hours) |  ≈ 90 core‑hours → \~USD 90–180 |
| **Storage** (all CSVs)                        |  ≈ 20 GB                        |

*Tips*

* Start with 2‑D CFD slices before 3‑D.
* Use SimScale’s free Community plan for public prototypes; upgrade for private data.
* Throttle API jobs to avoid quota overrun.

---

## <a name="references"></a>7. Key References

1. **WNTR documentation** – [https://wntr.readthedocs.io](https://wntr.readthedocs.io)
2. **SimScale Python SDK** – [https://api.simscale.com](https://api.simscale.com)
3. Multi‑fidelity distillation survey: Raissi et al., *“Deep Multi‑Fidelity Gaussian Processes”*, 2019.
4. LeakG3PD generator – [https://github.com/leak-ml/LeakG3PD](https://github.com/leak-ml/LeakG3PD)

