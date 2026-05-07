# Module 1E: Function Generator / Arbitrary Waveform Generator

## Module Design Document

**Version:** 1.1 (May 2026, Option A redesign)
**Module ID:** 1E
**Tier:** 1
**Status:** In Design
**Parent SDD section:** 7.5.5 of the [PMVB System Design Document](../system-design/System_Design_Document.html#module-1e-function-generator-arbitrary-waveform-generator)

---

## Table of Contents

- [1. Theory of Operation](#theory-of-operation)
  - [Signal generation chain](#signal-generation-chain)
  - [Why AD9742 with Pico parallel streaming](#why-ad9742-with-pico-parallel-streaming)
  - [Output impedance switching](#output-impedance-switching)
  - [Synchronization and trigger](#synchronization-and-trigger)
- [2. Functional Block Diagram](#functional-block-diagram)
- [3. Schematic Notes (high-level; full schematic in KiCad)](#schematic-notes-high-level-full-schematic-in-kicad)
  - [DAC output stage and current-to-voltage conversion](#dac-output-stage-and-current-to-voltage-conversion)
  - [Reconstruction filter](#reconstruction-filter)
  - [Op-amp differential-to-single-ended converter](#op-amp-differential-to-single-ended-converter)
  - [Op-amp supply](#op-amp-supply)
  - [Impedance switching](#impedance-switching)
  - [Decoupling](#decoupling)
- [4. Pin Assignments](#pin-assignments)
  - [Pico 2 W parallel data + clock to AD9742](#pico-2-w-parallel-data-clock-to-ad9742)
  - [Pico 2 W relay control](#pico-2-w-relay-control)
  - [Pico 2 W trigger I/O](#pico-2-w-trigger-io)
  - [Pico 2 W power](#pico-2-w-power)
  - [AD9742 pinout summary](#ad9742-pinout-summary)
  - [AD8056 op-amp output stage](#ad8056-op-amp-output-stage)
- [5. Specifications (matching SDD Table 7-27)](#specifications-matching-sdd-table-7-27)
- [6. Sample Applications](#sample-applications)
  - [6.1 Single-tone sine generation](#single-tone-sine-generation)
  - [6.2 Swept sine for THD measurement (paired with Module 2E)](#swept-sine-for-thd-measurement-paired-with-module-2e)
  - [6.3 Multitone for IMD (intermodulation distortion)](#multitone-for-imd-intermodulation-distortion)
  - [6.4 White noise for noise-floor characterization](#white-noise-for-noise-floor-characterization)
  - [6.5 Clock generation for digital characterization](#clock-generation-for-digital-characterization)
  - [6.6 Bias-mode voltage injection](#bias-mode-voltage-injection)
- [7. Bill of Materials](#bill-of-materials)
- [8. Calibration Procedure](#calibration-procedure)
  - [8.1 DC offset calibration](#dc-offset-calibration)
  - [8.2 Gain calibration](#gain-calibration)
  - [8.3 Frequency calibration](#frequency-calibration)
  - [8.4 Reconstruction filter passband flatness](#reconstruction-filter-passband-flatness)
- [9. Bring-Up Checklist](#bring-up-checklist)
- [10. Known Issues and Future Work](#known-issues-and-future-work)
- [11. References](#references)

---

## 1. Theory of Operation

Module 1E generates analog waveforms for amplifier characterization, in-ear monitor and headset testing, clock generation for digital interfaces, and any test sequence that needs a controlled stimulus into a DUT. The module is built on a single Pico 2 W presenting as a USB-TMC instrument to the Pi 5 host; calibration constants live in the Pico's onboard 4 MB flash. The design pairs the Pico with an Analog Devices AD9742 12-bit 210 MSPS current-mode DAC, an AD8056 high-speed differential-to-single-ended op-amp output stage, a 5th-order Butterworth reconstruction filter, and a three-position output impedance switch (50 Ω / 600 Ω / 10 kΩ). Single-channel BNC output, ±10 V swing, DC to 10 MHz signal range.

### Signal generation chain

A precomputed waveform sample table sits in the Pico's flash or is generated on the fly in SRAM. The Pico's PIO (Programmable I/O) state machine, paired with DMA, streams 12-bit samples to the AD9742's parallel data port at up to 50 MSPS. The AD9742 outputs a complementary differential current pair (IOUTA, IOUTB), which drives 25 Ω termination resistors to AGND to convert the current to a differential voltage. A 5th-order Butterworth low-pass filter at ~12 MHz cutoff smooths the DAC stair-step output, then an AD8056 op-amp configured as a differential receiver with gain converts to single-ended ±10 V output. The single-ended signal passes through a three-position impedance switch (50 Ω / 600 Ω / 10 kΩ) to a front-panel BNC.

For a 1 kHz sine wave at 50 MSPS DAC update rate, the waveform has 50,000 samples per cycle: many orders of magnitude above the Nyquist requirement, with quantization noise dominated by DAC INL/DNL rather than oversampling ratio. At 10 MHz output the DAC produces 5 samples per cycle (5× oversampling), and the reconstruction filter rejects the first image (at 50 - 10 = 40 MHz) by approximately 50 dB. A ±10 V sine at 10 MHz requires roughly 628 V/µs slew at the op-amp output, well within the AD8056's 1400 V/µs spec.

### Why AD9742 with Pico parallel streaming

The AD9742 is a current-output DAC with a parallel data interface: 12 data bits plus a clock line. This trades two things for two others, compared to a SPI-driven DAC like the MCP4922:

- **Trade 1 (positive)**: parallel interface lets the DAC update at the Pico's full PIO clock rate (up to 150 MHz on RP2350), enabling 50+ MSPS update rates that SPI cannot reach. Bandwidth of the resulting analog output stretches into the 10s of MHz.
- **Trade 2 (positive)**: TSSOP package (28-pin, 0.65 mm pitch, leaded gull-wing) is hand-solderable with a basic iron and flux. Compare to AD9106's 32-LFCSP, which requires hot-air rework or oven reflow.
- **Trade 3 (negative)**: parallel interface consumes more Pico GPIOs (13 versus 4 for SPI). Pico has the GPIOs to spare; this is a non-issue in practice.
- **Trade 4 (negative)**: the Pico has to stream samples in real time at the DAC update rate — there's no internal pattern memory or DDS engine on the AD9742. At 50 MSPS this requires PIO + DMA at ~75 MB/s sustained throughput, which is at the edge of what RP2350 can do reliably; in practice the module runs at 30 to 50 MSPS depending on waveform complexity.

For practical AWG use cases (single tones via phase-accumulator DDS in firmware, swept sines, multitone, pseudo-random noise, simple arbitrary waveforms up to a few kSPS), the trade-offs land favorably on the AD9742's side.

### Output impedance switching

The output stage can present three source impedances, selected by three SPST reed relays gated by Pico GPIOs (only one energized at a time):

- **50 Ω** — for connection to oscilloscope inputs (50 Ω termination), RF gear, or any device with a 50 Ω input.
- **600 Ω** — legacy audio standard, useful for connection to vintage transformer-coupled audio gear or high-impedance balanced lines.
- **10 kΩ** — current-limited "bias" mode for safely applying a voltage to a digital pin, calibration test point, or other high-impedance node. The 10 kΩ series resistor caps fault current at V/R (e.g., 10 V into a short = 1 mA), well below the input clamp-diode rating of any 3.3 V or 5 V CMOS digital input.

### Synchronization and trigger

The module exposes one auxiliary digital output that can be configured as a sync pulse (rising edge at the start of each waveform period) or a continuous gate. This output ties to the chassis-wide trigger bus (see SDD section 11.4) so captures on Module 2E (Mixed-Signal Digitizer) can be synchronized to AWG output without software-arming jitter. The module also accepts a trigger input from the same bus, allowing the AWG to start its waveform on an external event.

## 2. Functional Block Diagram

Module 1E is documented across three figures: a system-level view showing where the module sits in the PMVB chassis, the AD9742 internal block diagram (from the datasheet), and a typical-application schematic showing the parallel data path, current-to-voltage conversion, reconstruction filter, op-amp output stage, and impedance switching.

**Figure 1E-1: Module 1E system context (system block diagram)**

<img src="../figures/modules/1e_system_context.svg"
     alt="Module 1E in the v1.0 PMVB chassis"
     style="width: 100%; height: auto; display: block; margin: 0 auto;">

**Figure 1E-2: AD9742 internal functional block diagram**

<img src="../figures/modules/1e_ad9742_internal.svg"
     alt="AD9742 internal block diagram, redrawn from datasheet Rev. C"
     style="width: 100%; height: auto; display: block; margin: 0 auto;">

*Source: AD9742 datasheet (Rev. C), page 1. Analog Devices Inc. Used under fair-use citation for technical reference.*

**Figure 1E-3: Module 1E typical application schematic**

<img src="../figures/modules/1e_typical_app.svg"
     alt="Pico 2 W → AD9742 → reconstruction filter → AD8056 → 50/600/10kΩ relay → BNC"
     style="width: 100%; height: auto; display: block; margin: 0 auto;">

*Schematic shows the parallel data interface from Pico to AD9742, the differential current outputs through 25 Ω termination resistors and the 5th-order Butterworth reconstruction filter, the AD8056 differential-to-single-ended op-amp converter with gain to ±10 V, and the three-position SP3T impedance-switching network feeding the BNC output.*

## 3. Schematic Notes (high-level; full schematic in KiCad)

### DAC output stage and current-to-voltage conversion

The AD9742 produces complementary differential currents at IOUTA and IOUTB. Full-scale current is set by an external precision resistor at the FSADJ pin (per the AD9742 datasheet section "Reference Operation"); we use a 1.91 kΩ ±0.1% resistor to set FS_CUR ≈ 20 mA. Each output drives a 25 Ω 0.1% precision termination resistor to AGND. The differential voltage swing at the op-amp input is therefore ±0.5 V peak across each 25 Ω resistor (depending on the digital input code), giving a 1 V differential signal that the op-amp scales to the final ±10 V single-ended output.

### Reconstruction filter

A 5th-order Butterworth low-pass filter sits between the DAC's differential output and the op-amp input. Cutoff at ~12 MHz, characteristic impedance 50 Ω. Standard ladder topology (L–C–L–C–L) with the values:

- L1 = L3 = L5 ≈ 1.0 µH (Coilcraft 0805LS-102XJRC, ±5 %)
- C2 = C4 ≈ 470 pF (Murata GCM1885C1H471JA16D, C0G ±5 %)

Tabulated normalized Butterworth values are in the Analog Devices DAC application note AN-282 and equivalents; tolerances on these passives directly affect passband ripple, so 5 % C0G capacitors and ±5 % wirewound chip inductors are the minimum specifications. Better tolerances (1 % caps, 2 % inductors) produce flatter passband response if budget permits.

### Op-amp differential-to-single-ended converter

The AD8056 channel A is configured as a difference amplifier:

- IN+ receives the filtered IOUTA signal through R_in1 (1 kΩ)
- IN− receives the filtered IOUTB signal through R_in2 (1 kΩ)
- Feedback resistor R_fb (10 kΩ) sets the differential gain to 10
- Reference resistor (10 kΩ) at IN+ to ground sets the common-mode rejection

Differential gain of 10 takes the 1 V differential filter output to 10 V single-ended. Adjustment to the gain network shifts the output range; for ±10 V output, the gain is 20 (factoring in the differential signal centered at midscale).

### Op-amp supply

The AD8056 is rated for ±5 V to ±13.5 V supply (refer to the datasheet Absolute Maximum Ratings). We power it from the chassis TX300 PSU's +12 V and -12 V rails, giving comfortable headroom for the ±10 V output swing. The op-amp's 1400 V/µs slew rate provides about 2.2× margin for the worst-case full-amplitude 10 MHz sine (which needs 628 V/µs), so harmonic distortion from slew limiting is negligible.

### Impedance switching

Three Coto 9007-05-01 SPST-NO reed relays (5 V coils, signal-grade) sit between the op-amp output and three different series resistors:

- Relay 1 → 50 Ω 1% resistor → BNC center
- Relay 2 → 600 Ω 1% resistor → BNC center
- Relay 3 → 10 kΩ 1% resistor → BNC center

Pico GPIO drives each relay through a 2N3904 transistor and a 1N4148 flyback diode across the coil. The Pico firmware enforces "only one relay energized at a time" so the BNC sees exactly one source impedance. Reed relays were chosen over solid-state analog switches because their on-resistance is essentially zero (no series error added to the 50 Ω termination), they have signal-grade isolation in the off state, and they handle bidirectional signals cleanly.

### Decoupling

Every IC supply pin gets a 0.1 µF X7R 0603 ceramic placed within 4 mm of the pin. The AD9742 additionally gets a 10 µF 10 V X5R bulk cap at the supply entry per the datasheet section "Power Supply Bypassing." AVDD and DVDD pins are decoupled separately with their own 0.1 µF caps to avoid digital noise coupling into the analog reference. The op-amp gets two 0.1 µF caps (one per supply rail, V+ and V−) plus a shared 10 µF bulk cap.

## 4. Pin Assignments

### Pico 2 W parallel data + clock to AD9742

The Pico's PIO state machine drives 12 contiguous GPIOs as the parallel data bus, plus one GPIO for the DAC clock. Using GP0–GP11 for data keeps the PIO instruction simple (single shift register output to a contiguous pin range).

| Pico Pin | GP | Function | AD9742 Pin | Notes |
|---|---|---|---|---|
| 1 | GP0 | DB0 (LSB) | 12 | parallel data bit 0 |
| 2 | GP1 | DB1 | 11 | parallel data bit 1 |
| 4 | GP2 | DB2 | 10 | parallel data bit 2 |
| 5 | GP3 | DB3 | 9 | parallel data bit 3 |
| 6 | GP4 | DB4 | 8 | parallel data bit 4 |
| 7 | GP5 | DB5 | 7 | parallel data bit 5 |
| 9 | GP6 | DB6 | 6 | parallel data bit 6 |
| 10 | GP7 | DB7 | 5 | parallel data bit 7 |
| 11 | GP8 | DB8 | 4 | parallel data bit 8 |
| 12 | GP9 | DB9 | 3 | parallel data bit 9 |
| 14 | GP10 | DB10 | 2 | parallel data bit 10 |
| 15 | GP11 | DB11 (MSB) | 1 | parallel data bit 11 |
| 16 | GP12 | CLOCK | 17 | DAC sample clock from Pico PIO |

### Pico 2 W relay control

| Pico Pin | GP | Function | Notes |
|---|---|---|---|
| 17 | GP13 | RELAY_50 | drives 2N3904 base for 50 Ω relay coil |
| 19 | GP14 | RELAY_600 | drives 2N3904 base for 600 Ω relay coil |
| 20 | GP15 | RELAY_10K | drives 2N3904 base for 10 kΩ relay coil |

Firmware enforces mutually exclusive relay energizing.

### Pico 2 W trigger I/O

| Pico Pin | GP | Function | Notes |
|---|---|---|---|
| 21 | GP16 | SYNC_OUT | sync pulse to chassis trigger bus (configurable as period sync or continuous gate) |
| 22 | GP17 | TRIG_IN | trigger input from chassis bus, for synchronized stimulus start |

### Pico 2 W power

| Pico Pin | Function | Notes |
|---|---|---|
| 39 | VSYS | 5 V from chassis (USB-bus-powered via Pi 5 USB hub) |
| 38 | GND | shared chassis ground |
| 36 | 3V3_OUT | for AD9742 AVDD/DVDD (after local LC filtering) |

### AD9742 pinout summary

| AD9742 Pin | Function | Connects to |
|---|---|---|
| 1–12 | DB11–DB0 (parallel data, MSB to LSB) | Pico GP11–GP0 |
| 17 | CLOCK | Pico GP12 |
| 18 | DVDD | +3.3 V from Pico (after LC filter to suppress digital noise) |
| 19 | DCOM | digital ground |
| 20 | AVDD | +3.3 V (separately filtered) |
| 21 | IOUTA | 25 Ω termination to AGND, then to reconstruction filter input |
| 22 | ACOM | analog ground |
| 23 | IOUTB | 25 Ω termination to AGND, then to reconstruction filter input |
| 24 | FSADJ | 1.91 kΩ ±0.1 % to AGND, sets full-scale current |
| 25 | REFIO | internal reference; 0.1 µF decoupling to AGND |
| 26 | REFLO | reference low; tied to AGND |
| 27 | SLEEP | tied to GND for normal operation |
| 28 | MODE | tied to GND for parallel mode |

### AD8056 op-amp output stage

| AD8056 Pin | Function | Connects to |
|---|---|---|
| 1 | OUT (channel A) | reconstruction filter output → impedance-switching relay matrix |
| 2 | IN− (channel A) | filter IOUTB output through R_in2 (1 kΩ) and feedback R_fb (10 kΩ) |
| 3 | IN+ (channel A) | filter IOUTA output through R_in1 (1 kΩ); R_ref (10 kΩ) to GND for CMRR |
| 4 | V− | −12 V from chassis TX300 |
| 5 | IN+ (channel B) | unused; tied to GND |
| 6 | IN− (channel B) | unused; tied to OUT (channel B) |
| 7 | OUT (channel B) | unused (channel B reserved for v1.1 stereo or differential output) |
| 8 | V+ | +12 V from chassis TX300 |

## 5. Specifications (matching SDD Table 7-27)

| Parameter | Value |
|---|---|
| DAC | AD9742, 12-bit, 210 MSPS-capable |
| DAC update rate (operating) | 30–50 MSPS via Pico PIO + DMA |
| Channels | 1 single-ended output (channel B reserved for v1.1) |
| Standard waveforms | sine (DDS), square, triangle, ramp, noise, multitone, arbitrary |
| Arbitrary waveform depth | up to ~256 K samples (limited by Pico SRAM) |
| Output range | ±10 V |
| Output impedance (selectable) | 50 Ω / 600 Ω / 10 kΩ via SPST reed relays |
| Frequency range | DC to 10 MHz |
| Frequency accuracy | ±20 ppm crystal; ±2 ppm with external 10 MHz reference via chassis trigger bus |
| Amplitude resolution | 12-bit (~5 mV at 20 V FS span) |
| Slew rate | 1400 V/µs (AD8056-limited) |
| THD (typical, audio band) | < 0.1 % (limited by DAC INL/DNL) |
| Reconstruction filter | 5th-order Butterworth, ~12 MHz cutoff, ~50 dB image rejection at 40 MHz |

## 6. Sample Applications

### 6.1 Single-tone sine generation

```python
import pyvisa
rm = pyvisa.ResourceManager('@py')
awg = rm.open_resource('USB::0xCAFE::0x4001::PMVB1E::INSTR')
awg.write('OUTP:IMP 50')             # select 50 Ω output impedance
awg.write('SOUR:FUNC SIN')
awg.write('SOUR:FREQ 1000')
awg.write('SOUR:VOLT 1.0')           # 1 V peak-to-peak
awg.write('OUTP ON')
input('Press Enter to stop...')
awg.write('OUTP OFF')
awg.close()
```

### 6.2 Swept sine for THD measurement (paired with Module 2E)

```python
import numpy as np
from scipy.fft import rfft, rfftfreq

awg = open_module('1E')
scope = open_module('2E')

awg.write('OUTP:IMP 50')
frequencies = np.logspace(np.log10(20), np.log10(20000), 31)
results = []

for f in frequencies:
    awg.write(f'SOUR:FUNC SIN; SOUR:FREQ {f}; SOUR:VOLT 1.0; OUTP ON')
    scope.write('DIG:CONF 0, 5.0, AC; DIG:RATE 1000000; DIG:DEPTH 100000; DIG:ARM')
    samples = np.array(scope.query_binary_values('DIG:DATA? 0', datatype='f'))
    spectrum = np.abs(rfft(samples))
    freqs = rfftfreq(len(samples), 1/1e6)
    fund_bin = np.argmin(np.abs(freqs - f))
    fund = spectrum[fund_bin]
    harms = [spectrum[np.argmin(np.abs(freqs - f*n))] for n in range(2, 6)]
    thd = np.sqrt(sum(h**2 for h in harms)) / fund
    results.append((f, thd))
    awg.write('OUTP OFF')

for f, thd in results:
    print(f'{f:8.1f} Hz: THD = {thd*100:.3f}%')
```

### 6.3 Multitone for IMD (intermodulation distortion)

```python
awg.write('OUTP:IMP 50')
awg.write('SOUR:MULT:UPLD [1000, 1100], [0.5, 0.5]')   # SMPTE-style 60/7 ratio variant
awg.write('SOUR:VOLT 1.0; OUTP ON')
# Capture and FFT-analyze for sum/difference products near 100 Hz, 2.0 kHz, etc.
```

### 6.4 White noise for noise-floor characterization

```python
awg.write('OUTP:IMP 50')
awg.write('SOUR:FUNC NOIS')
awg.write('SOUR:VOLT 0.5; OUTP ON')
# Capture, integrate over band, compute spectral density
```

### 6.5 Clock generation for digital characterization

A square wave at 1–10 MHz is useful for clocking external digital interfaces during characterization, or as a stimulus to a clock-recovery circuit for jitter measurement.

```python
awg.write('OUTP:IMP 50')              # 50 Ω back-termination for digital signal integrity
awg.write('SOUR:FUNC SQU')
awg.write('SOUR:FREQ 5000000')        # 5 MHz
awg.write('SOUR:VOLT 3.3')            # 3.3 V swing for CMOS receivers
awg.write('OUTP ON')
```

### 6.6 Bias-mode voltage injection

For applying a controlled voltage to a digital pin or high-impedance test point without risk of frying the DUT, switch to 10 kΩ output impedance and set a DC level. Fault current at any short is capped at V/10kΩ (e.g., 1 mA at 10 V), well below the input clamp-diode rating of any 3.3 V or 5 V CMOS digital input.

```python
awg.write('OUTP:IMP 10K')             # 10 kΩ current-limited mode
awg.write('SOUR:FUNC DC')
awg.write('SOUR:VOLT 2.5')            # 2.5 V DC bias
awg.write('OUTP ON')
```

## 7. Bill of Materials

Cross-referenced to Digi-Key (primary; Mouser was not accessible during this audit), with Microcenter for the Pico 2 W. Last verified May 2026.

| Item | Manufacturer P/N | Supplier | Supplier P/N | Qty | Unit Cost | Notes |
|---|---|---|---|---|---|---|
| Raspberry Pi Pico 2 W | Raspberry Pi SC1633 | Microcenter | SKU 687384 | 1 | $5.99 | RP2350 host MCU; Microcenter sale price |
| 12-bit 210 MSPS DAC | Analog Devices AD9742ARUZ | Digi-Key | AD9742ARUZ | 1 | $14.80 | 28-TSSOP, hand-solderable |
| Dual VFB op-amp 1400 V/µs | Analog Devices AD8056ARZ | Digi-Key | AD8056ARZ-ND | 1 | $6.27 | SOIC-8, channel A used; channel B reserved |
| Reed relay SPST-NO 5 V coil | Coto Technology 9007-05-01 | Digi-Key | 306-1004-ND (or current equivalent) | 3 | $2.09 | three for SP3T impedance switching |
| 2N3904 NPN BJT (relay driver) | onsemi 2N3904BU | Digi-Key | 2N3904FS-ND | 3 | $0.10 | TO-92, one per relay |
| 1N4148 small-signal diode (relay flyback) | onsemi 1N4148 | Digi-Key | 1N4148FSCT-ND | 3 | $0.05 | DO-35, one per relay |
| Precision resistor 25.0 Ω 0.1 % 0805 (DAC term) | Vishay PTN0805E25R0BST1 | Digi-Key | PTN0805E25R0BST1 | 2 | (verify direct) | 25 Ω matched pair across IOUTA/IOUTB |
| Precision resistor 50 Ω 1 % 0805 | Yageo RC0805FR-0750RL | Digi-Key | (verify direct) | 1 | ~$0.10 | 50 Ω output Z |
| Precision resistor 600 Ω 1 % 0805 | Yageo RC0805FR-07600RL | Digi-Key | (verify direct) | 1 | ~$0.10 | 600 Ω output Z |
| Precision resistor 10 kΩ 1 % 0805 | Yageo RC0805FR-0710KL | Digi-Key | RC0805FR-0710KL | 1 | ~$0.10 | 10 kΩ output Z |
| FSADJ resistor 1.91 kΩ 0.1 % 0805 | Vishay TNPW08051K91BEEA | Digi-Key | (verify direct) | 1 | (verify direct) | sets AD9742 full-scale current |
| Reconstruction filter inductor 1 µH 0805 ±5 % | Coilcraft 0805LS-102XJRC | Digi-Key | (search direct) | 6 | $2.01 | three per channel; one channel built initially |
| Reconstruction filter cap 470 pF C0G 0603 ±5 % | Murata GCM1885C1H471JA16D | Digi-Key | (search direct) | 4 | (verify direct) | two per channel |
| Op-amp gain network resistors 1 % 0805 | Yageo RC0805FR-07 series | Digi-Key | (verify direct) | 4 | ~$0.10 | R_in1, R_in2, R_fb, R_ref |
| Bypass cap 0.1 µF X7R 0603 50 V | Yageo CC0603KRX7R9BB104 | Digi-Key | 311-1366-1-ND (or equiv) | 10 | $0.08 | per IC supply pin |
| Bulk cap 10 µF X5R 0805 10 V | Yageo CC0805KKX5R8BB106 (or Murata GRM21BR71A106KA73L) | Digi-Key | (search direct) | 4 | (verify direct) | DAC, op-amp, +12V, -12V supply rails |
| BNC panel-mount jack 50 Ω | Amphenol RF 031-5538 | Digi-Key | 031-5538 | 1 | (verify direct) | front-panel output |
| 3D-printed enclosure | n/a | n/a | n/a | 1 | ~$1 | PETG print, ~10 g |
| Hookup wire, headers, perfboard or custom PCB | various | various | various | n/a | TBD | full schematic in KiCad; PCB fab quote pending |
| **Module BOM total (verified portions, single-quantity Digi-Key/Microcenter)** | | | | | **~$53** | excludes PCB fab and items still pending direct verification |

Items marked "(verify direct)" are commodity passives and connectors whose prices were not extracted from Digi-Key's JS-rendered pages during the BOM audit. They are in stock at Digi-Key and individually cost less than $5; total impact on the module BOM is under $15.

## 8. Calibration Procedure

After module assembly, calibrate against a Fluke 87V (or equivalent calibrated DMM) and a 10 MHz GPSDO reference (or external function generator's calibrated output) using the following procedure.

### 8.1 DC offset calibration

1. Configure: `OUTP:IMP 50; SOUR:FUNC DC; SOUR:VOLT 0.0; OUTP ON`.
2. Wait for output to settle (1 s).
3. Measure the DC level on the output BNC with the Fluke 87V.
4. Adjust the op-amp's CMRR-trim resistor until the measured DC level reads within ±5 mV of 0 V (or store the offset as a software calibration constant).
5. Record via SCPI: `CALC:CAL:OFFS 0, <millivolts>`.

### 8.2 Gain calibration

1. Configure: `OUTP:IMP 50; SOUR:FUNC SIN; SOUR:FREQ 1000; SOUR:VOLT 10.0` (peak-to-peak).
2. Connect the output through a known-good 50 Ω terminator to a calibrated scope or Fluke and measure the actual peak-to-peak voltage.
3. Compute the gain error: `gain_correction = 10.0 / measured_pk_pk`.
4. Store: `CALC:CAL:GAIN 0, <gain_correction>`.

### 8.3 Frequency calibration

If the chassis trigger bus carries an external 10 MHz GPSDO reference, the firmware can phase-lock against it and update the frequency-divider constant accordingly. Without an external reference, the Pico's crystal is rated ±20 ppm, which is ±200 Hz at 10 MHz; for most characterization work this is below the tolerance of the DUT under test.

### 8.4 Reconstruction filter passband flatness

1. Sweep `SOUR:FREQ` from 1 kHz to 10 MHz at constant `SOUR:VOLT 1.0`.
2. Capture the peak-to-peak amplitude with Module 2E (or external scope) at each frequency.
3. Plot the magnitude response. The 5th-order Butterworth should show ≤ ±0.5 dB ripple across DC to ~10 MHz.
4. If the response shows excessive ripple (component tolerance issue), trim the filter inductors or substitute tighter-tolerance caps. Record the calibrated frequency response in the Pico flash so frequency-dependent corrections can be applied per the SCPI gain command.

## 9. Bring-Up Checklist

In order, on first power-up:

1. **Visual inspection.** Check polarity of every electrolytic and tantalum cap. Check op-amp orientation (notch toward pin 1). Check AD9742 pin 1 orientation. Check relay coil polarity. Verify no shorts between the parallel data bus and adjacent traces.
2. **Power-on without DUT.** Apply +5 V (Pico) and +12 V/−12 V (op-amp). Measure current draw: should be ~50 mA total at idle (Pico ~30 mA, AD9742 ~30 mA digital + 20 mA analog, AD8056 ~10 mA). If higher, pull power and find the short.
3. **Pico boots.** Watch the onboard LED; it should heartbeat. Pico USB enumerates as USB-TMC: `lsusb` on the host should show the PMVB device.
4. **DAC midscale test.** Send `SOUR:FUNC DC; SOUR:VOLT 0.0; OUTP ON`. With the Pico writing midscale codes (0x800) to the AD9742, IOUTA and IOUTB should each carry ~10 mA (half of FS_CUR ≈ 20 mA), giving a differential voltage of ≈ 0 V across the 25 Ω terminations. At the op-amp output, the reading should be 0 V ± 50 mV.
5. **Full-scale test.** Send `SOUR:FUNC DC; SOUR:VOLT 10.0; OUTP ON`. Pico drives the DAC to all-ones (0xFFF). Op-amp output should be near +10 V.
6. **Sweep test (audio band).** `OUTP:IMP 50; SOUR:FUNC SIN; SOUR:FREQ 1000; SOUR:VOLT 5.0; OUTP ON`. Output should be a 5 Vpp sine at 1 kHz on a scope, no visible distortion.
7. **Sweep test (HF band).** Repeat at 1 MHz and 10 MHz. Verify amplitude is within ±0.5 dB of the audio reading.
8. **Frequency response.** Sweep 20 Hz to 10 MHz and verify amplitude flatness within ±0.5 dB across the band.
9. **THD (audio band).** At 1 kHz, 1 Vrms output, capture with Module 2E and verify THD < 0.1 %.
10. **Spectral purity (HF band).** At 5 MHz, 1 Vrms output, capture with Module 2E and verify the first-image rejection is ≥ 40 dB. The first image should appear near the DAC update rate minus 5 MHz.
11. **Impedance switch test.** Cycle through `OUTP:IMP 50`, `OUTP:IMP 600`, `OUTP:IMP 10K`. For each, drive the DUT with a known voltage and measure source impedance with a known load.
12. **Calibration.** Run section 8 procedures. Save calibration constants to Pico flash.
13. **PyVISA-sim parity check.** Run the same SCPI command sequence against the simulator backend and verify behavior matches.

## 10. Known Issues and Future Work

(To be populated as the module is built.)

- The Pico's PIO + DMA can sustain 50 MSPS DAC update rate for short bursts, but sustained operation may require dropping to 30–40 MSPS. Characterize Pico bandwidth ceiling early in firmware bring-up; document the achievable update rate as a v1.0 specification.
- The AD9742 produces a small mid-scale glitch (datasheet specifies < 5 pV·s typical) at code transitions. For low-distortion audio work below 100 kHz this is well below the noise floor; for HF work it manifests as a small spurious tone at the DAC update rate. Mitigation is a careful reconstruction filter design.
- AD8056 channel B is unused in v1.0. A v1.1 enhancement could repurpose it as a stereo output (using a second AD9742) or as a buffered sync signal.
- The 5th-order Butterworth reconstruction filter component tolerances directly affect passband flatness. Initial builds may need tightened tolerance (1 % caps, 2 % inductors) on critical positions if the as-built ripple exceeds ±0.5 dB.
- A Tier 2 (FPGA-driven) variant of this module could push bandwidth to 50 MHz by replacing the AD9742 with a faster parallel DAC (AD9744 at 14-bit 210 MSPS) clocked from the Tang Primer 25K. That's a separate future module, not a v1.x evolution of this one.

## 11. References

- [Analog Devices AD9742 datasheet](https://www.analog.com/en/products/ad9742.html)
- [Analog Devices AD8056 datasheet](https://www.analog.com/en/products/ad8056.html)
- [Coto Technology 9007 series reed relay datasheet](https://www.cotorelay.com/product/9007-series/)
- [Raspberry Pi Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf)
- [Analog Devices Application Note AN-282 (DAC reconstruction filters)](https://www.analog.com/en/resources/app-notes/an-282.html)
- [PMVB System Design Document, section 7.5.5](../system-design/System_Design_Document.html#module-1e-function-generator-arbitrary-waveform-generator)
