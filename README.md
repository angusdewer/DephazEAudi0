 # DephazEAudi0
### Φ³-based Topological Audio Reconstruction System

**DephazEAudi0** is a real-time audio processing system that treats digital sound not as a sequence of amplitude values, but as a set of geometric states.

Instead of operating in the time or frequency domain, the system embeds each PCM sample into a Φ³-anchored geometric space, evaluates its relation to an ideal spherical symmetry, and projects the resulting information back into the audible domain.

This is not an effect, not a model, and not an emulation.  
It operates in a different computational space.

---

## What the system does

Conventional digital audio processing represents sound as discrete amplitude steps.  
While effective, this representation is inherently angular and discontinuous at the numerical level.

DephazEAudi0 approaches the signal differently:

- each individual sample is treated as a continuous geometric entity  
- the sample is embedded into a three-dimensional, anchored space  
- the system compares the state against an ideal spherical symmetry  
- audible output is derived from the controlled breaking of that symmetry  

> The sound is not distorted — it is reorganized.

---

## Resolving PCM angularity

PCM sampling is, by nature:
- discrete  
- angular  
- non-continuous in geometric terms  

DephazEAudi0 resolves this by projecting each sample into a micro-precision anchored space where:

- the ideal condition is perfect spherical symmetry  
- real audio always deviates from this condition  
- the deviation becomes a measurable geometric quantity  

Processing is based on **how symmetry is broken**, not on amplitude thresholds or envelopes.

---

## The Dephaze relation

At the core of the system lies a single closed-form relation (Ξ) that:

- compares spatial extent with internal curvature  
- operates on an irrational Φ³ order, avoiding periodic resonance  
- is evaluated per sample, without temporal memory  

This relation directly computes geometric properties that cannot be fully derived using conventional DSP approaches based on envelopes, filters, or spectral decomposition.

This is not a matter of optimization, but of computational paradigm.

---

## What it does not use

DephazEAudi0 does not employ:

- attack or release times  
- thresholds  
- lookahead  
- frequency band separation  
- time-domain smoothing  

All dynamic behavior emerges from instantaneous geometric relationships.

---

## Audible characteristics


Changes are perceived in how the sound:
- maintains coherence at high dynamics  
- reveals internal structure without harshness  
- avoids periodic distortion artifacts  
- remains spatially consistent  


---

## Runtime environment

The archive contains:
- a Python reference implementation  
- a Rust-based executable  
- a visualization illustrating the topological behavior  

Both implementations use the same mathematical core and operate in real time.

---

### Common requirements

- Windows 10 / 11 (64-bit)
- functional audio input and output
- virtual audio cable (e.g. VB-Cable)

The virtual cable currently serves as a routing and hosting layer.

---

### Python version

Requirements:
- Python 3.10+ (64-bit recommended)

Dependencies:

- pip install numpy sounddevice pyqt5 pyqtgraph
Run:

 
 
- python DephazEAudi0.py
Features:

- selectable input and output audio devices

- fixed sample rate: 48 kHz

- block size: 256 samples

- real-time operation via virtual audio cable

### Rust version
- precompiled executable (.exe)

- no Rust toolchain required

- selectable input and output devices

- real-time operation via virtual audio cable

### Audio routing example
 
- DAW / Audio source
        ↓
- Virtual Audio Cable 
        ↓
- DephazEAudi0 (Input → Processing → Output)
        ↓
- Working Output
        ↓
- Monitoring / DAW
This routing is not part of the algorithm itself, only the current execution environment.

### Notes
Python and Rust implementations share the same mathematical formulation

minor floating-point differences may occur across platforms

the focus of the project is the observable behavior of the system
## Citation

If you use or reference this work, please cite:

**Angus Dewer (2026)**  
*DephazEAudi0 — Φ³-based Topological Audio Reconstruction*  
Zenodo. https://doi.org/10.5281/zenodo.18244991

