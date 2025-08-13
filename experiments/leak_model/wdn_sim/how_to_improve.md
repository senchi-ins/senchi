# Hydraulics Event Coupling – Current State & Future Ideas

The term **hydraulics event coupling** refers to keeping EPANET’s hydraulic
solution in-step with time-varying failures (growing leaks, progressive
blockages, valve operations, etc.).  In other words: _whenever an event changes
the network, we immediately re-solve hydraulics so flow, velocity and pressure
reflect that change_.

## What’s already implemented
1. **Per-timestep update loop** – inside `HouseSimulator.run()` the heavy EPANET
   branch executes:  
   ```python
   self.scheduler.apply_events_to_network(t_h)  # updates emitters & diameters
   self.hydraulics.run_hydraulics(self.resolution_seconds)
   ```
   for every timestep `t_h`.  Therefore:
   * Leak `emitter_coeff` grows with time ⇒ higher demand & pressure loss.  
   * Blockage `pipe.diameter` shrinks ⇒ head-loss and velocity increase.

2. **Light-mode analytics** – the lightweight path adds extra leak discharge
   directly to the demand array and recalculates velocity analytically
   (Darcy-Weisbach not required), giving a fast approximation for unit tests
   and CI.

3. **Static pre-run adjustments** – before the loop starts we call
   `_apply_static_event_effects()` so that any events active at _t = 0_ are
   already applied to the EPANET network.

## Why the TODO was left open
* The current implementation samples only the `Pipe` link and `House` junction.
  If you later need pressures at every branch (`Kitchen`, `Bathroom2`, …) those
  columns should be extracted too.
* Re-assigning `pipe.diameter` every few seconds is fine for moderate
  simulations.  For long or highly granular runs EPANET caching may complain;
  we can mitigate by cloning the network or resetting hydraulic options.
* No regression tests yet assert that the simulated head-loss matches
  theoretical expectations (velocity ∝ 1/**D²**, head-loss ∝ 1/**D⁵** for
  turbulent flow).

## Possible future improvements
1. **Multi-node sampling**
   * Store pressure/velocity for all fixture junctions and pipes.
2. **Continuous emitter update for blockages**
   * Instead of directly shrinking `pipe.diameter`, model blockage as a minor
     loss coefficient so that original pipe metadata stays intact.
3. **Performance optimisations**
   * Cache EPANET hydraulics objects or use WNTR’s pressure-dependent demand
     mode to avoid full re-solve every second.
4. **Physics validation tests**
   * Add PyTest cases that check expected scaling laws for head-loss and
     cross-validate against analytical calculations for a straight pipe.
5. **Logging & visualisation hooks**
   * Emit a `dict` per timestep (or a Polars row) with active event metadata to
     make debugging easier.

## Transient (TSNet) integration – current behaviour
TSNet is optional and runs **only** when `enable_tsnet=True` *and* the event schedule contains a `PRESSURE_BURST` leak.

* After the steady‐state EPANET loop finishes the simulator calls `quick_transient(...)` once, simulating a 2-second water-hammer burst at the leak node.
* Instead of dumping the entire high-frequency pressure trace we compress it into the three ultrasonic meter proxy columns already defined by the schema:
  * `downstream_wave_time`
  * `upstream_wave_time`
  * `delta_time`
  For five samples after the burst onset we write a small non-zero pulse; elsewhere the columns stay **NaN**.  That keeps file size tiny but still gives an ML model a clear transient signature to learn from.
* Designers who need richer transients can either
  1. map real Δt values from `trans_df` into the columns, or
  2. save `trans_df` as a separate Parquet alongside the main file.

### Future ideas
1. Support valve-closure events in addition to bursts.
2. Store peak dP/dt, wave speed or other engineered features instead of the synthetic pulse.
3. Batch all bursts at the end of the house-day into one longer TSNet run for efficiency.

---

_This document captures the current status so future contributors know where
hydraulics event coupling stands and what can be enhanced next._

