# 5G Managerial Round — Interview Prep Guide
> **For:** Tieto Final Round | **When:** Tomorrow 3:30 PM | **Level:** Manager/Director
> **Read time:** ~25 mins | Focus: Concepts, use cases, big picture thinking

---

## 1. Why Do We Need 5G? — The Compelling Answer

This is likely the first or second question. Don't just say "faster speeds" — that's a shallow answer. Here's the complete picture:

### The Three Fundamental Drivers

**Driver 1 — Exponential Data Growth**
Global mobile data traffic has been doubling every 2 years. By 2025, there were over 18 billion connected devices globally — more devices than people. 4G simply cannot carry this load. The spectrum is congested, speeds are degrading, and latency is unpredictable. 5G provides the capacity headroom needed for the next decade.

**Driver 2 — New Use Cases 4G Cannot Support**
4G was designed for smartphones — human-to-human and human-to-internet connectivity. The next wave of technology requires machine-to-machine communication at a scale and latency 4G cannot deliver:
- A self-driving car needs to react in milliseconds — 4G's 30–50ms latency is too slow; a car travels 1.4 metres in 50ms at 100 km/h
- A factory with 1,000 robots all communicating simultaneously — 4G can't support that device density
- Remote surgery requires sub-1ms latency and 100% reliability — impossible on 4G

**Driver 3 — Economic Opportunity**
5G is estimated to contribute $13.2 trillion to the global economy by 2035 (Qualcomm study). Industries like manufacturing, healthcare, agriculture, logistics, and entertainment are being transformed. Countries and companies that deploy 5G first gain competitive advantage.

### The One-Line Answer for the Manager:
> *"We need 5G because 4G was built for smartphones. 5G is built for everything — connecting not just people but machines, vehicles, factories, and entire industries in ways that were physically impossible before."*

---

## 2. What's New in 5G? — 4G vs 5G Comparison

### The Big Three Pillars of 5G (3GPP Definition)

| Pillar 	| Name 										| What It Means 				| 4G Equivalent |
|---|---|---|---|
| **eMBB** 	| Enhanced Mobile Broadband 				| Faster speeds for people 		| Basic broadband |
| **URLLC** | Ultra-Reliable Low Latency Communications | Mission-critical reliability 	| Not supported |
| **mMTC** 	| Massive Machine Type Communications 		| Billions of IoT devices 		| Limited IoT |

---

### Key Technical Differences — 4G LTE vs 5G NR

| Parameter 					| 4G LTE 										| 5G NR 										| Improvement |
|---|---|---|---|
| **Peak download speed** 		| ~150 Mbps (typical) / 1 Gbps (theoretical) 	| ~1 Gbps (typical) / 20 Gbps (theoretical) 	| 20x faster |
| **Latency** 					| 30–50 ms 										| 1–10 ms (sub-1ms for URLLC) 					| 10–50x lower |
| **Device density** 			| ~100,000 devices/km² 							| ~1,000,000 devices/km² 						| 10x more devices |
| **Spectrum** 					| Sub-6 GHz only 								| Sub-6 GHz + mmWave (24–100 GHz) 				| Much wider spectrum |
| **Bandwidth per channel** 	| Up to 20 MHz 									| Up to 400 MHz (FR2) 							| 20x more bandwidth |
| **Network slicing** 			| Not supported 								| Fully supported 								| New capability |
| **Beamforming** 				| Basic (4 antennas) 							| Massive MIMO (64–256 antennas) 				| Dramatically better |
| **Architecture** 				| EPC (Evolved Packet Core) 					| 5GC (5G Core) + Service Based Architecture 	| Cloud-native |

---

### What is 5G NR? (New Radio)
5G NR is the new air interface standard defined by 3GPP from Release 15 onwards. "NR" distinguishes it from LTE (the 4G air interface). Key innovations in NR:

**Flexible Numerology**
4G used a fixed subcarrier spacing of 15 kHz. 5G NR introduces flexible numerology (μ = 0,1,2,3,4) with subcarrier spacings of 15, 30, 60, 120, 240 kHz. This allows 5G to efficiently serve very different use cases — from wide-area coverage (15 kHz) to ultra-low latency mmWave (120 kHz).

**Massive MIMO**
4G base stations typically had 2–8 antennas. 5G gNB uses 32–256 antennas (Massive MIMO) enabling advanced beamforming — the signal follows the user like a spotlight rather than flooding the cell like a floodlight. This dramatically improves spectral efficiency and capacity.

**mmWave (Millimetre Wave)**
5G opens up spectrum above 24 GHz (FR2 — Frequency Range 2) for the first time in mobile networks. This spectrum was previously unused for mobile because of the challenge of propagation. mmWave enables multi-Gbps speeds at short range — transforming indoor coverage, stadiums, and dense urban areas.

**Network Slicing**
5G core enables the same physical network to be divided into multiple virtual networks (slices), each with different characteristics. A self-driving car slice gets ultra-low latency. A smart meter slice gets low power, low cost. A video streaming slice gets high bandwidth. All on the same infrastructure simultaneously.

**Standalone (SA) vs Non-Standalone (NSA)**
- **NSA (Release 15):** 5G NR radio + 4G LTE core — quick to deploy, uses existing 4G infrastructure
- **SA (Release 16+):** 5G NR radio + 5G Core — full 5G, enables network slicing, true URLLC, MEC

---

## 3. 5G Frequency Bands — FR1 and FR2

| Range 	| Name 			| Frequencies 			| Characteristics |
|---|---|---|---|
| **FR1** 	| Sub-6 GHz 	| 410 MHz – 7.125 GHz 	| Wide coverage, good propagation, lower speeds |
| **FR2** 	| mmWave 		| 24.25 GHz – 52.6 GHz  | Short range, very high speeds, line-of-sight |

**Why both matter:**
- FR1 provides coverage — like 4G, covers cities and rural areas
- FR2 provides capacity — hotspots, stadiums, indoor enterprise, fixed wireless access

---

## 4. 5G Use Cases — The Complete Picture

### Use Case Category 1: eMBB (Enhanced Mobile Broadband)

> *"A good eMBB example is high-quality video streaming in crowded environments where many users simultaneously consume large amounts of data."*
> *"VR and cloud gaming are strong eMBB use cases because they require very high and stable data rates along with low latency for smooth user interaction."*

**Fixed Wireless Access (FWA)**
Replacing home broadband cables with 5G wireless. Telcos install a 5G router at home, delivering 500 Mbps–1 Gbps — faster than most cable broadband. Already commercially deployed by Verizon, T-Mobile, Reliance Jio in India.

**Immersive Media — AR/VR**
High-quality AR/VR requires 1 Gbps+ throughput and <20ms latency. 5G enables untethered VR headsets streaming 8K video in real time. Applications: remote training, virtual showrooms, gaming, live events.

**Enhanced Mobile Video**
4K/8K video streaming, multi-camera live sports, cloud gaming (Xbox Cloud Gaming, GeForce NOW) — all enabled by 5G's high throughput.

**Real Example:** Reliance Jio's True5G — India's largest 5G deployment, covering 50+ cities with eMBB services.

---

### Use Case Category 2: URLLC (Ultra-Reliable Low Latency)

**Connected and Autonomous Vehicles (CAV)**
- Vehicle-to-Everything (V2X) communication: car ↔ car, car ↔ infrastructure, car ↔ pedestrian
- Requires: <1ms latency, 99.9999% reliability
- Use: collision avoidance, traffic coordination, remote driving
- Example: Ericsson and Volvo testing 5G-connected trucks in Sweden

**Remote Surgery / Telemedicine**
- A surgeon in Mumbai operates on a patient in a rural village using robotic arms
- Requires: sub-5ms latency, haptic feedback, ultra-HD video
- Example: First 5G remote surgery performed in China in 2019

**Industrial Automation — Smart Factory**
- Wireless robot control replacing cables in factories
- Requires: <5ms latency, 99.999% reliability, high device density
- Example: Ericsson's smart factory in Tallinn, Estonia — fully 5G connected
- Example: BMW using 5G for real-time quality control in manufacturing

**Critical Infrastructure**
- Power grid control, water management, emergency services
- 5G's network slicing ensures a dedicated, prioritised slice for critical services

---

### Use Case Category 3: mMTC (Massive Machine Type Communications)

**Smart Cities**
- Smart street lighting (adjusts based on traffic)
- Smart parking (sensors report availability)
- Environmental monitoring (air quality, noise levels)
- Smart waste management (bins report when full)
- Thousands of sensors per city block — 5G's device density handles this

**Smart Agriculture**
- Soil sensors monitoring moisture, temperature, nutrients
- Drone coordination for crop monitoring and spraying
- Livestock tracking
- Weather stations throughout farms
- Example: John Deere using 5G for precision agriculture

**Smart Metering**
- Electricity, gas, water meters reporting every 15 minutes
- Millions of meters per city — only 5G's mMTC supports this density
- Enables dynamic pricing, fault detection, energy efficiency

**Supply Chain & Logistics**
- Every package, pallet, and container tracked in real time
- Warehouse robots coordinated wirelessly
- Example: DHL using 5G for real-time shipment tracking

---

### Use Case Category 4: Emerging — Beyond Release 15

**Private 5G Networks**
Companies deploying their own private 5G networks inside factories, airports, ports, and campuses — like having your own mobile network. Provides security, reliability, and customisation impossible on public networks.

**Mobile Edge Computing (MEC)**
Processing compute tasks at the edge of the network (near the base station) rather than in a distant data centre. Reduces latency to microseconds for applications that need it. Essential for AR/VR, autonomous vehicles, real-time analytics.

**5G for Industry 4.0 (5G-ACIA)**
The 5G Alliance for Connected Industries and Automation defines how 5G enables the 4th industrial revolution — combining 5G with AI, robotics, and digital twins.

**Network as a Service**
5G network slicing allows telcos to sell network capabilities as a service — guaranteed bandwidth, guaranteed latency, guaranteed reliability — like a service level agreement for connectivity.

---

## 5. 5G Architecture — What Changed from 4G

<* In 4G, the entire base station (eNB) is one box doing everything — radio, physical layer processing, scheduling, RRC, PDCP all in one vendor-proprietary unit. If you buy Nokia eNB, everything inside is Nokia. No flexibility, no mix-and-match.

<* 5G Architecture — CU / DU / RU Split
<* 5G deliberately breaks the base station into three separate units:
<* RU (Radio Unit) — sits at the antenna. Handles RF, analogue conversion, and the lowest PHY layer (FFT, IFFT, PRACH detection). Connects to DU over fronthaul (eCPRI).
<* DU (Distributed Unit) — handles real-time processing. Lower PHY (channel estimation, equalisation, HARQ), MAC, and RLC. Must be close to RU due to latency constraints.
<* CU (Central Unit) — handles non-real-time. PDCP, RRC, SDAP. Can sit in a data centre far away. Further split into CU-CP (control plane) and CU-UP (user plane)

### 4G Architecture (EPC — Evolved Packet Core)

```
[UE] → [eNB] → [S-GW] → [P-GW] → [Internet]
              ↘ [MME] (control)
```

- Monolithic core network functions
- Hardware-based, proprietary
- Control and user plane mixed together

### 5G Architecture (5GC — 5G Core)

```
[UE] → [gNB] → [UPF] → [Internet]
              ↘ [AMF][SMF][PCF][UDM]... (control — microservices)
```

Key changes:
- **Service Based Architecture (SBA):** Core functions are microservices communicating via APIs — like a cloud application, not a telecom box
- **Control/User Plane Separation (CUPS):** AMF handles control; UPF handles data — can be placed independently for MEC
- **Cloud-Native:** Runs on standard servers, containers, Kubernetes — not proprietary telecom hardware
- **Network Slicing:** End-to-end slices from RAN through core

---

## 6. 5G RAN Architecture — What's New

### From eNB to gNB
- 4G base station = **eNB** (evolved Node B)
- 5G base station = **gNB** (next generation Node B)

### The gNB Split — CU and DU
In 5G the base station is split into:
- **gNB-CU** (Central Unit): Handles PDCP, RRC — can be centralised in a data centre
- **gNB-DU** (Distributed Unit): Handles RLC, MAC, PHY — deployed close to the antenna

This enables centralisation and cloud-RAN deployments.

### O-RAN — Open RAN
Further splits the gNB-DU into:
- **O-RU** (Radio Unit): Low PHY + RF — at the tower
- **O-DU** (Distributed Unit): High PHY + MAC — at data centre
- **O-CU** (Central Unit): RRC/PDCP — cloud

Connected by open interfaces (Fronthaul = eCPRI, F1, Xn) enabling multi-vendor networks.

---

## 7. 5G in India — Relevant Context for the Interview

Since this is a Bangalore interview, showing knowledge of India's 5G journey is impressive:

**India 5G Rollout:**
- Spectrum auctioned in August 2022 — Jio, Airtel, Vi, Adani all participated
- Jio: True5G launched October 2022 — SA deployment, 33 bands, 700 MHz + 3.5 GHz + 26 GHz
- Airtel: 5G launched November 2022 — NSA initially, migrating to SA
- Coverage: 5G now covers 700+ cities across India as of 2025

**India's 5G Opportunity:**
- India has 1.4 billion people — largest mobile market after China
- 5G expected to contribute $450 billion to India's GDP by 2035
- Smart cities, digital agriculture, manufacturing — all key use cases for India

**Homegrown 5G:**
- IIT Madras developed India's first indigenous 5G RAN stack (O-RAN compliant)
- Tata Consultancy Services developing 5G solutions for Indian market
- BSNL deploying homegrown 4G/5G stack developed by TCS/C-DoT

---

## 8. 5G Generations Timeline — Context

| Generation 		| Year 		| Peak Speed 		| Key Innovation |
|---|---|---|---|
| 1G 				| 1980s 	| Analog voice 		| First mobile phone calls |
| 2G (GSM) 			| 1991 		| 9.6 Kbps 			| Digital voice, SMS |
| 3G (UMTS/HSPA) 	| 2001 		| 42 Mbps 			| Mobile internet, video calls |
| 4G (LTE) 			| 2009 		| 150 Mbps typical 	| Smartphone era, streaming |
| **5G (NR)** 		| **2019** 	| **1–20 Gbps** 	| **IoT, URLLC, industry** |
| 6G (expected) 	| 2030 		| 1 Tbps 			| AI-native, THz spectrum, NTN |

---

## 9. 5G Challenges — Shows Balanced Thinking

A manager will be impressed if you acknowledge challenges, not just benefits:

**Coverage challenge:**
mmWave has excellent speed but poor propagation — walls, rain, leaves block it. Dense small cell deployments needed — expensive.

**Cost of deployment:**
5G infrastructure requires significant CAPEX. Operators need clear ROI — which is why eMBB consumer use cases came first before industrial URLLC.

**Device ecosystem:**
5G devices took time to arrive at affordable price points. Now mainstream (iPhone 12+, most Android flagships).

**Spectrum availability:**
Sub-6 GHz spectrum is scarce and expensive. Countries are at different stages of clearing spectrum for 5G.

**Latency promise vs reality:**
True sub-1ms URLLC latency requires Standalone 5G + MEC. Many early 5G deployments are NSA — they get speed but not the full latency benefit.

**Energy consumption:**
5G base stations consume significantly more power than 4G — Massive MIMO and wider bandwidth increase power usage. Ericsson, Nokia, and Huawei are actively working on energy-efficient 5G RAN (AI-based sleep modes, etc.)

---

## 10. Likely Managerial Round Questions — With Answers

---

**Q: "In simple terms, what is 5G and why does it matter?"**

> *"5G is the 5th generation of mobile network technology — defined by 3GPP from Release 15. What makes 5G fundamentally different from 4G isn't just speed — it's versatility. 5G was designed to serve three completely different types of communication: very fast broadband for people, ultra-reliable low latency for machines and critical systems, and mMTC for massive connectivity for billions of IoT devices. 4G was built for smartphones. 5G is built for the entire connected world — including industries, vehicles, hospitals, and smart cities."*

---

**Q: "What are the key differences between 4G and 5G?"**

> *"The main differences are in three areas. First, performance — 5G offers 20x faster peak speeds and 10–50x lower latency than 4G. Second, technology — 5G introduces new spectrum (mmWave), Massive MIMO with hundreds of antennas, flexible numerology, and network slicing — all new concepts not in 4G. Third, architecture — 5G has a cloud-native core built on microservices and APIs, whereas 4G core was monolithic and hardware-based. From my work at the physical layer, the most significant technical change is the introduction of flexible numerology and Massive MIMO which fundamentally changed how we design the PHY pipeline."*

---

**Q: "What 5G use cases excite you the most?"**

> *"From a personal perspective, I find two use cases most compelling. First, URLLC for industrial automation — the idea that a factory floor can replace all its cables with wireless 5G connections, enabling fully flexible manufacturing, is genuinely transformative. Second, connected vehicles — the safety implications of vehicles communicating with each other and infrastructure in sub-1ms is profound. From a professional standpoint, what excites me is that both of these use cases fundamentally depend on the physical layer doing its job perfectly — which is exactly where my expertise lies."*

> *"Applications like remote surgery highlight how communication reliability and latency are no longer just performance metrics but safety requirements."*

> *"V2X is exciting because communication reliability and latency can directly affect safety. PHY performance becomes critical in high-mobility conditions where synchronization, channel tracking, and scheduling must work efficiently."*

> "*Applications like VR gaming excite me because user experience directly depends on PHY throughput and latency. Efficient scheduling, beamforming, and low retransmission delay are very important to avoid lag and motion sickness."*

**Q: "Where do you see 5G going in the next 5 years?"**

> *"I see three major directions. First, 5G SA (Standalone) deployments will finally deliver on the original URLLC and network slicing promise — many operators are still on NSA. Second, private 5G networks will proliferate in manufacturing, logistics, and enterprise — this is a significant market opportunity for companies like Tieto helping clients build these. Third, 5G Advanced (Release 18 onwards) will bring AI-native RAN, improved energy efficiency, and early NTN capabilities. And on the horizon, 6G research is active — though commercial deployment is 2030+. The industry is shifting from 5G deployment to 5G monetisation, which creates demand for software-first, feature-rich RAN — exactly what Tieto's engineering practice delivers. AI-driven network optimization becoming much more important, especially for applications like XR, autonomous systems, and real-time analytics."*

---

**Q: "Why do you want to work on 5G specifically?"**

> *"I've been working in 5G NR physical layer development since May 2018 — it chose me as much as I chose it. Starting from implementing the first 3GPP Release 15 stack at CommAgility, through DFE and FreeRTOS firmware work, to real-time ARM and x86 PHY optimisation at E-Space — I've built my entire career around this technology. What keeps me excited is that 5G is still evolving — Releases 17, 18, 19 are bringing NTN, AI-RAN, and RedCap. The physical layer is where the magic happens — it's the boundary between mathematics and radio waves, and getting it right means millions of devices connect reliably. That combination of intellectual challenge and real-world impact is why I'm here."*

---

**Q: "What do you know about Tieto's work in 5G?"**

> *"Tieto Tech Consulting has a strong 5G RAN engineering practice working across L1, L2, and L3 for Tier-1 clients in the Nordic region — which means Ericsson and Nokia ecosystem work. I know Tieto attended MWC 2026 and published insights on the shift to AI-native networks and 5G SA monetisation. I also know the team is actively growing — hiring across all RAN layers simultaneously — which suggests a significant active engagement. I'm particularly interested in Tieto's positioning around O-RAN and software-defined RAN, which aligns with where the industry is heading and where my experience with FAPI/nFAPI interfaces and GPP-based L1 development is most relevant."*

---

## 11. Quick Reference — Numbers to Know

| Metric 					| 5G Value 				| Context |
|---|---|---|
| Peak download speed 		| 20 Gbps 				| Theoretical FR2 |
| Typical download 			| 1–3 Gbps 				| FR1 good conditions |
| Latency (eMBB) 			| 10 ms 				| User experience |
| Latency (URLLC) 			| < 1 ms 				| Industrial/critical |
| Device density 			| 1M devices/km² 		| mMTC |
| 5G spectrum FR1 			| 410 MHz – 7.125 GHz 	| Coverage |
| 5G spectrum FR2 			| 24.25 – 52.6 GHz 		| Capacity |
| 3GPP Release (first 5G) 	| Release 15 (2018) 	| NSA |
| 3GPP Release (SA 5G) 		| Release 16 (2020) 	| Full 5G |
| 3GPP Release (NTN) 		| Release 17 (2022) 	| Satellite |
| 3GPP Release (AI-RAN) 	| Release 18 (2024) 	| 5G Advanced |

---

## 12. Final Tips for Tomorrow's Managerial Round

**Tone:** This is a business/strategic conversation, not a deep technical drill. Speak in clear, confident language. Avoid diving into bit-level PHY details unless specifically asked.

**Connect to business impact:** Managers think in terms of value delivered, not technical specs. Always connect your answers to what it means for operators, enterprises, or end users.

**Show enthusiasm:** 5G is genuinely exciting — let that come through. A manager wants someone who cares about the domain, not just the salary.

**Ask a smart question at the end:**
> *"What is the most technically challenging 5G project Tieto's RAN team is currently working on, and what does success look like for that project?"*

This shows you're thinking about contribution, not just the job title.

**Relax:** You've cleared two technical rounds with engineers who know 5G deeply. A managerial round on general 5G concepts is well within your comfort zone. You've been living and breathing this for 8+ years.

---

*Good luck tomorrow at 3:30 PM. You've earned this round — go in confident. 🚀*
