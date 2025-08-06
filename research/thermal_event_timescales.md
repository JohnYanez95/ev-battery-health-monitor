# Thermal Event Timescales and BMS Thermal Management in EV Battery Packs

## 1. Thermal Event Progression Timescales

### Gradual Overheating (Cooling System Failure)

In a scenario where the active cooling system fails or is absent, an EV battery's temperature rise is relatively slow (compared to a thermal runaway). Under normal driving loads, it often takes **tens of minutes to hours** for a pack to heat from nominal (~25–30 °C) up to dangerous levels. For example, a Nissan Leaf (which has no active liquid cooling) only pushed its battery into the "red" temperature zone (roughly >50 °C) after an entire day of driving and multiple fast-charging sessions¹ ². In Phoenix summer heat (~45 °C ambient), one Leaf owner noted the battery was still below the critical zone after sitting all day, only climbing into red after fast charging³. This indicates that without cooling, even in hot climates the pack warms gradually unless high-current charging/discharging is involved.

By contrast, our simulation's 82-second rise from 50 °C to 60 °C is extremely aggressive – such a rapid 10 °C jump in ~1.3 minutes would typically require an unrealistic combination of a very high heat generation and very low thermal mass or cooling. In real vehicles, reaching critical thresholds (50→60 °C) would more likely take on the order of **several minutes (under severe abuse) to hours (under moderate stress)**, not mere seconds. Our 82 s progression might only be conceivable in a worst-case failure or testing scenario (e.g. coolant loss plus sustained maximum current) – it is on the fast end of plausibility.

Automakers generally design so that during extreme but realistic abuse (e.g. track driving, or climbing a mountain on a hot day with a failed coolant pump) the battery temperature would still take a few minutes to rise into the danger zone, giving the BMS time to respond. In summary, gradual overheating due to cooling loss tends to unfold over **dozens of seconds to many minutes**, not instantaneously. We should likely dial back our thermal ramp speed unless we're specifically simulating a catastrophic failure.

### Rapid Thermal Events (Cell Failure & Propagation)

If an individual cell suffers an internal failure and goes into **thermal runaway**, the timescales become much more abrupt. A single cell in runaway can heat to hundreds of °C within seconds, and if unchecked this can induce neighboring cells to follow suit in a chain reaction⁴. Laboratory tests show that once thermal runaway starts, a battery pack's heat release can peak in seconds – e.g. a small e-scooter pack reached a 1.1 MW fire peak in 13 seconds after the first cell went exothermic⁴. Cell-to-cell propagation in the absence of barriers can occur on the order of **seconds to under a minute**, as hot ejecta and flames from the failing cell ignite its neighbors⁵.

Because of this, safety standards now demand a delay: for instance, Chinese EV regulations (GB/T 38031) require a **5-minute thermal propagation delay** from the moment a battery hazard is detected to the point where passengers would be in danger⁶ ⁷. In other words, packs must be designed to withstand a thermal runaway without spreading for at least 5 minutes, giving occupants time to evacuate. Many modern EVs aim to meet this "five-minute rule", typically by using thermal barriers between cells, venting strategies, etc.⁸ ⁷.

If those measures fail, however, thermal spikes are extremely fast – one source notes the first few minutes of a thermal event are "explosive and violent," and without mitigation an entire module can be engulfed in well under a minute⁹ ⁵. To answer the question: during cell-to-cell propagation, temperature can spike almost instantaneously in the affected module (a matter of seconds). With good design, propagation might be slowed to a crawl (minutes or halted entirely), but without it, rapid thermal events are measured in seconds. Our monitoring system should therefore be capable of detecting **very fast temperature excursions (on the order of 1 °C per second or more)** as an indication of cell failure – a dramatically different regime from normal operation.

### Charging-Induced Heating (Normal vs. Abnormal Rates)

During DC fast charging, lithium-ion batteries heat up due to internal resistance and charging inefficiency. Under normal conditions, the BMS actively manages this: packs are often pre-heated to an optimal temperature (typically around 45–55 °C) to reduce impedance, and cooling systems work to hold the cells in a safe range¹⁰. For example, Tesla vehicles will heat the battery to roughly 50 °C prior to Supercharging and then use the coolant/AC system to stabilize around that range, since fast charging is actually fastest when cells are warm (but not too hot)¹⁰ ¹¹.

In a well-designed system, the temperature rise during a single fast-charge session is modest – perhaps on the order of **10–20 °C over 20–30 minutes**, with active cooling mitigating the peak. Real-world data from passive-cooled EVs illustrates normal vs. abnormal: early Nissan Leafs would often see battery temps climb into the high 40s °C after one aggressive fast charge (and then BMS would throttle the charge rate)¹². Pushing further – multiple back-to-back fast charges – could drive the temp into the red zone (~50–60 °C), as happened in "#Rapidgate" cases, but this took on the order of **an hour or more of cumulative charging/driving**¹³.

In contrast, abnormal heating (e.g. if cooling fails during charging or an overcurrent fault) could lead to much higher rise rates. An extreme U.S. DOE study noted that without proper thermal management, cell core temperatures could exceed 270 °C in 10 minutes of fast charging – essentially a thermal runaway scenario rather than normal operation. (No production EV would allow this; it's a lab stress test.) In practical terms, **normal DCFC might raise battery temperature at a few degrees Celsius per minute at most**, whereas an unsafe or fault condition could see the temperature climbing **multiple °C per minute or even per second** (which would immediately trigger failsafes).

So, our model should reflect that "normal" charging-induced heating is relatively slow and managed, while abnormal spikes are a big red flag. If our simulation's extreme test shows ~82 s from warning to shutdown (50→60 °C) during charging, that suggests an abnormally high heating rate. In reality, hitting emergency shutdown mid-charge in ~1–2 minutes would imply something like a cooling system outage or serious battery fault. Typically, a vehicle would have already cut or tapered the charging current well before it got that hot that fast.

Thus, an 82-second rise to critical under charge is not a normal scenario – it's closer to a worst-case abuse test. It may be possible in extreme conditions, but we should label it as such (e.g. "simulated cooling failure during 250 kW charge in 40 °C ambient"). For a more typical fast charge in hot weather, expect slower progression (perhaps tens of minutes to approach thermal limits, if at all, thanks to cooling and current tapering).

### Realism of an 82-Second Warning→Shutdown Progression

As hinted above, an 82 s progression from 50 °C to 60 °C is faster than what automotive engineers would consider normal, even under "extreme" use. It falls into an edge case category. Real EV packs have significant thermal inertia and multiple safeguards. For instance, in track driving (sustained high discharge, which is very stressful), a Tesla Model 3 Performance took a couple of laps before it began throttling due to battery overheat – the pack temperature warnings appeared and then power was curtailed as it climbed past ~55 °C towards 60 °C¹⁴ ¹⁵. This happened over **several minutes**, not seconds. That vehicle did eventually hit ~60 °C and strongly limit power, but only after some time of abuse, and it cooled down gradually after exiting the track¹⁶ ¹⁷.

Another example: high-power EVs ascending long grades in hot weather will typically take **many minutes** to heat soak the battery to the point of derating. Therefore, if our simulation shows an ~1 minute from first thermal warning to forced shutdown under "extreme conditions," we should verify what those conditions represent. It might be realistic only if we assume a major cooling failure or unrealistically high internal resistance.

Our current parameter tweaks (using 0.2 Ω internal resistance and only 120 kg thermal mass) indeed create a very severe scenario. In reality, a Tesla Model 3 pack's internal resistance is much lower (on the order of milliohms per cell, translating to perhaps ~0.01–0.02 Ω at the pack level under high load¹⁵), and the effective thermal mass of the system is higher. So, bottom line: **82 seconds from 50 to 60 °C is on the unrealistic side for a whole-pack gradual overheat**. It would be more believable for a localized thermal runaway onset (where a failing cell can hit those temps in seconds) or a contrived test.

For model credibility, we may want to slow this down to a more authentic timescale (several minutes) for an extreme abuse case. That said, preserving a fast-rising scenario could still be useful to demonstrate the monitoring system's response in a "fault" scenario – just be sure to label it clearly as an off-nominal, worst-case event.

**Note on Battery Chemistry**: The above applies primarily to Nickel Manganese Cobalt (NMC/NCM) chemistries like the Tesla Model 3's NCA/NCM811 cells. Lithium Iron Phosphate (LFP) cells have different thermal behavior – notably, LFP cells are more thermally stable and resist runaway longer. An LFP cell typically doesn't enter thermal runaway until ~200–270 °C (much higher than ~150–180 °C for NMC)¹⁸ ¹⁹, and when it does, the temperature rise rate is slower/less violent¹⁹. This means an LFP pack is less likely to experience a rapid chain reaction fire; however, LFP will still overheat and degrade if pushed beyond ~60 °C for long. In practice, BMS temperature limits for LFP packs are similar to NMC – you'll still see warnings in the 50s °C and shutdown around 60 °C, because above that you risk damaging the pack even if it might not combust. So, while LFP chemistry gives some extra safety margin (and some EVs with LFP packs may be a bit more tolerant of high temps day-to-day), the timescales of thermal events under abuse aren't dramatically different in the early stages. LFP can buy you a little more time before a worst-case failure, but a monitoring system should treat ~60 °C as dangerous for any Li-ion chemistry.

## 2. Industry-Standard Thermal Thresholds

### Typical BMS Temperature Thresholds (Warning, Limit, Shutdown)

Real EV Battery Management Systems have fairly consistent temperature guardrails, often in the same ballpark as our model (50 °C, 55 °C, 60 °C). In fact, **60 °C is commonly treated as an upper safety limit** in many EV designs¹¹. For instance, Tesla pack temperatures around 55 °C are already considered "very high normal", and crossing ~60 °C will trigger aggressive power limitations¹⁵ ¹⁷. In a documented case, a Tesla Model 3 Performance on a racetrack began flashing warning messages as cell temps approached the mid-50s °C, and by the time the battery exceeded 60 °C (140 °F) the car intentionally cut back power output significantly to protect itself¹⁴ ¹⁷. The technicians confirmed the vehicle was designed to do so – >60 °C was considered "overheated" and outside normal operating bounds¹⁵ ¹⁷.

Likewise, Nissan's Leaf (Gen1/Gen2) uses a temperature gauge with 12 bars where the red zone starts roughly around 10–11 bars (approximately 50–55 °C) and 12 bars corresponds to ~60 °C or above. The Leaf's control logic will start limiting power once the pack gets well into the red zone; by the time it hits the final bar, the car enters a severe limp mode ("turtle" icon)²⁰ ²¹. According to a Leaf expert: at 10 bars (first red mark) the BMS begins reducing max motor power and regen; at 11 bars acceleration is heavily reduced (though the car can still hold highway speed), and if it reaches 12 bars the system will activate "turtle mode" (~25 mph max) as an ultimate protection²⁰ ²¹. This aligns very closely with our 50/55/60 °C stages (since ~10–11 bars roughly translates to ~50–55 °C and 12 bars ~60 °C+ in that vehicle).

Other manufacturers have similar thresholds: often ~45–50 °C is the point where cooling systems go to max and warnings may be logged, ~55 °C might trigger customer-visible alerts or reduced performance, and **~60 °C is typically the emergency cutoff range**. It's worth noting that 60 °C is also a common maximum in cell spec sheets and standards – e.g. many cells are rated 60 °C max for operation, and the USABC targets require EV batteries to survive up to 52–66 °C ambient conditions (which implies the pack itself might briefly see up to ~60 °C internally)²² ²³.

In short, our chosen thresholds (50/55/60 °C) are well-aligned with industry norms for NMC-based packs, and even LFP packs use similar cutoffs (even though the chemistry can handle a bit more without runaway, they still avoid exceeding ~60 °C because it accelerates degradation¹¹). So from a credibility standpoint, those numbers are solid.

### Temperature Rise Rates – "Concerning" vs. "Critical"

BMS not only monitors absolute temperature, but also the **rate of temperature increase**, as a rapidly rising cell temperature can indicate a problem (e.g. thermal runaway onset or a cooling system failure) even if the absolute value is not yet extreme. Industry data on specific °C/min thresholds is not always public, but we can infer:

- A slow creep (say, a few °C per hour) might just trigger a warning to service the cooling system
- A moderate rise (**several °C per minute**) will likely prompt immediate active cooling and possibly power reduction
- An extremely fast rise (**on the order of 1+ °C per second**) is an emergency (likely a cell in thermal runaway)

For example, if an EV pack is climbing at >1–2 °C per minute during use, that's a serious concern – under normal heavy loads with a functioning cooling system, you shouldn't see such a steep climb sustained. In our extreme simulation, the pack averaged ~0.12 °C per second (7.2 °C/min) during the warning-to-shutdown interval, which is indeed a critical rate. Real BMS would respond far earlier in such a case.

As evidence, fire-testing of battery packs shows that once a cell fails, the temperature skyrockets almost vertically – no surprise, BMS will cut everything off if a sensor reports an uncharacteristic jump. In everyday terms, one could say **"a few °C per minute" rise is concerning** (triggering aggressive cooling and possible power limit), whereas **"a few °C per second" is catastrophic** (triggering immediate shutdown). Some BMS algorithms use a ΔT/Δt trigger; for instance, a hypothetical BMS might say "if any module's temp rises >10 °C in one minute, flag a rapid thermal event." Our monitoring system design should incorporate this idea – not just absolute thresholds, but also watching for unusually fast heating.

Ambient conditions also factor into what rate is normal: on a 40 °C ambient day, the pack will naturally warm faster and start from a higher baseline, so the BMS might tolerate a slightly slower response (because everything is warmer) but it will also know the margin to the limit is smaller. In very cold ambient, a rapid rise might actually be expected when a cold battery is fast-charged (the heater is working hard), so context matters. Nonetheless, as a rule of thumb, **rise rates beyond a few °C/min under load are a red flag** in warm conditions, and **any double-digit °C per minute rise is treated as an emergency**.

### Ambient Temperature Effects on Thresholds

Ambient temperature doesn't usually change the absolute thermal limits of the cells (those are inherent), but it does affect how quickly those limits are reached and how the BMS calibrates its response. In high ambient (say ≥35–40 °C), the cooling system has less headroom to shed heat, so the BMS may enter thermal limiting sooner. Practically, this means at hot ambient temps, you might see the vehicle derate power at a slightly lower internal temperature or more proactively.

For instance, an EV in 40 °C weather might start to limit fast charging when the pack hits, say, 50 °C, whereas on a cool day it might allow 55 °C briefly, because in the hot case the heat cannot be easily rejected. Ambient heat essentially "pre-loads" the battery – a pack that's been sitting in 40 °C sun could already be at 40+ °C before you even drive. Automakers account for this: VW's ID.3, for example, will automatically kick on battery cooling at a threshold of ~32.5 °C battery temperature (since presumably on a hot day the battery can reach low-30s just from ambient soak)²⁴. Tesla also has features like cabin overheat protection and will run battery cooling even when parked if a high threshold is exceeded, to prevent heat soak.

Conversely, in cold ambient, BMS might actually heat the pack and raise it into the optimal zone. But importantly, **the upper safety thresholds (warning, power cut, etc.) in absolute terms usually remain the same** – e.g. 60 °C is dangerous whether it's hot or cold outside – what changes is how quickly you get there and how aggressively the system intervenes. In summary, ambient heat shortens the time to reach thresholds and forces the BMS to act sooner, but we generally do not see manufacturers saying "you can go to 65 °C if it's 45 °C out" – instead they try to avoid even hitting 60 by derating earlier in hot conditions.

Our model should reflect this by perhaps simulating a higher starting temperature and weaker cooling for hot climates (as we did with 40 °C ambient and a reduced cooling coefficient). That indeed showed a faster climb, which is realistic. So, yes – ambient conditions significantly affect how quickly thresholds are hit, but not the fundamental threshold values themselves.

### Alignment of 50/55/60 °C with Industry Standards

As noted, these specific values are very much in line with industry practice. Many EVs start battery thermal warnings around **50 °C**. Around **55 °C**, some will enter a reduced-power mode (or at least flash a warning to the driver). And by **60 °C**, virtually all will take drastic action (if not already) – either severely limiting power or in some cases initiating a shutdown to prevent damage.

These numbers also appear in battery guidelines: e.g. 45 °C is often cited as the upper end of the "optimal" zone¹⁰, with 60 °C being the edge of the "allowable" zone. The Amphenol Sensors EV thermal guide explicitly states: "Lithium-ion cells perform best between 15–45 °C… excessive heat above 60 °C increases safety risk"²⁵ ¹¹. Likewise, Battery University and others advise never charging above ~50 °C and note 60 °C as a critical limit for lithium batteries²⁶ ¹¹.

In short, our thresholds are well-chosen. They will be immediately familiar to automotive engineers, as they reflect common BMS setpoints. (And for LFP chemistry, while it's more tolerant before thermal runaway, manufacturers still stick in this range for operation – e.g. BYD and CATL LFP packs also aim to stay under ~55–60 °C for longevity.)

## 3. BMS Thermal Response Protocols

### Detection Speed and Monitoring Frequency

Modern BMS units monitor temperatures **continuously and in real-time**. Typically, there are multiple temperature sensors throughout a pack (each module might have one or more), and the BMS polls these on the order of **milliseconds to seconds**. For instance, if the pack is logging data at 1 Hz (once per second) for our telemetry, internally the BMS likely checks sensors even faster. So detection of an overheating condition is essentially immediate once a sensor crosses the threshold – **on the order of a second or less to trip a flag**.

In practice, the BMS firmware will have a debounce or smoothing (to avoid false alarms from momentary spikes), but any sustained exceedance of a threshold will be caught very quickly. In short, **thermal events do not sneak up on a modern BMS** – these systems are designed to be extremely vigilant since thermal management is safety-critical²⁷ ¹¹. So, if our simulation triggers at 50 °C, we should assume the real BMS would detect that at essentially t=31 s exactly (in our timeline) and start responding by t=32 s.

### Speed of Response and Power Limiting Strategies

Once a potential thermal issue is detected, BMS response can range from gentle to drastic depending on severity. In normal conditions, the first response is often to **activate cooling** – ramp up coolant pumps to maximum, turn fans to max, maybe even cool the cabin less to prioritize the battery cooling. If that isn't enough (or if cooling is already maxed out), the next step is **power limiting**.

Most EVs do not shut off power abruptly at the warning threshold; instead they gradually reduce available power to manage heat while trying to keep the vehicle driveable. For example, as mentioned, the Nissan Leaf progressively limits motor output as temperature climbs through the red zone – you feel acceleration getting sluggish, but the car still moves. Only if temperature keeps rising to critical does it go into turtle mode (drastic limp-home)²⁰ ²¹.

Similarly, Tesla (and others) will typically first cap the max power (e.g. you may see a yellow line on the power gauge indicating reduced peak kW). In the Model 3 track case, the car gave a warning at ~55 °C, then by the time it hit ~60 °C it had considerably pulled back power – the driver noted the car was limiting acceleration and even gave a brake temperature warning, effectively forcing a cool-down lap²¹. This was an automatic response from the BMS/inverter to protect components.

So **gradual reduction vs immediate cutoff**: Industry practice is gradual reduction for as long as possible, to give the driver a chance to notice and to preserve basic functionality. Immediate contactor open (cut-off) would only occur in an extreme emergency (e.g. cell voltage dropping to zero indicating a fire, or perhaps temperatures reaching truly unsafe levels beyond the scale – far above 60 °C). Under most overheat scenarios, the BMS tries to manage down the power smoothly.

### Multi-Stage Limiting

Many OEMs implement a **tiered approach** (which our model's notion of 70% → 30% → 0% power makes sense to emulate). For instance, we might imagine:

- **Stage 1**: At 50 °C, trigger a warning and maybe a slight reduction (e.g. limit charging current, or reduce available peak power by some percentage). The driver might see a message like "Battery warm – power output reduced" but still have, say, 70% of normal power.

- **Stage 2**: At 55 °C, if temperature continues to rise, aggressively limit power – perhaps allow only 30%–50% of full power. The Leaf example corresponds to this: by ~55 °C (11 bars) it could barely accelerate hard²⁰.

- **Stage 3**: At 60 °C, if the temperature hits this "emergency" threshold, the BMS would enact either an almost complete power cutoff or drop into a "limp mode" that is just enough to creep to the side of the road. In Leaf terms, that was turtle mode (~limiting speed to ~25 mph)²⁸. In other cars, it might be an error message and drastically reduced power, or even a shutdown to prevent damage if you're not driving (during charging, for instance, it would stop the charge).

Modeling a ~70% → ~30% → 0% (or turtle) progression is very much in line with these practices. It shows a graded response, which is how real BMS are programmed – they don't want to strand the driver unless absolutely necessary. So yes, we should implement stepped power limits at our warning, critical, and shutdown temps. This will make our simulation output look and behave more like a real vehicle's response.

### Response Timeframes and Recovery

When an over-temperature is detected, how quickly does the BMS act? Typically, the control action (like reducing current) is taken **immediately upon detection**. Electrical systems can throttle motor torque in milliseconds, so if a battery is overheating, the inverter/BMS can start reducing current on the very next control cycle. In human terms, you might notice within a few seconds that the car is losing power after the warning light comes on. So from the moment thresholds are crossed, the onset of limiting is extremely fast. The full effect (like dropping to 30% power) might be ramped in over, say, a few seconds to avoid a jarring cut, but it's still rapid. Modern EVs also often flash a warning to the driver ("Battery overheating, power reduced") as this happens.

After the event, **how long do thermal protection modes last and how do they recover?** That depends on cooling and how quickly the battery can shed heat. With an active cooling system, recovery can be relatively fast: once load is reduced, the coolant loop might bring the battery from, say, 55 °C down to 45 °C in a matter of minutes (perhaps 5–15 minutes, depending on ambient). In the Tesla track example, after a cooldown lap and some easier driving, the battery temp gradually came down and the car returned to normal operation later in the drive¹⁶.

If the car is stopped, it may even continue running coolant pumps or fans until the battery drops to a safe temperature (some EVs will run cooling after shut-off if the pack is very hot). By contrast, in a passively cooled system (or if the car is off), cooling could take a long time. The Leaf forum note mentions that it's rare for the battery to cool down much just by driving slowly – in 35–40 mph driving with high battery temp, the Leaf's pack was staying in the red (no active cooling to pull it down)²⁹ ¹². Essentially, in such cases the car will remain power-limited for an extended period. It might take an overnight park for the battery to fully cool back to ambient¹². Most liquid-cooled EVs fall somewhere in between – they can cool the battery, but it might still take several minutes to recover.

Many BMS will not immediately give back full power at the exact moment the threshold is cleared; they often require some **hysteresis** (cool down a few degrees below the threshold before restoring each stage) to avoid rapid oscillations. For example, if shutdown was at 60 °C, the BMS might wait until the pack falls to, say, 58 degrees before exiting turtle mode, and maybe below 50 °C before removing all limits. This can translate to a few minutes of limited performance even after the stressful event ends. In practice, drivers experience it as "I had to drive gently for 5–10 minutes until the car allowed full power again." Our model can approximate this by not instantly resuming full power at 59.9 °C, but perhaps building in a slight delay or temperature buffer for recovery.

### Examples of BMS Protocols

To give concrete instances:

- **Tesla**: Relies on robust liquid cooling; rarely hits thermal limits in daily use. In track or Supercharging scenarios, the car software preemptively cools or warms to keep battery in range. If it does overheat, it will prominently warn and reduce power. Tesla's philosophy is to preserve the battery, so it will cut power even if it inconveniences the driver (as seen on track)¹⁵ ¹⁷. They do not have a "turtle mode" per se, but a similar concept where power is heavily restricted.

- **Nissan Leaf**: With no active cooling, the BMS protocol heavily relies on power limiting. As discussed, it steps down power in stages as temperature bar count increases²⁰ ²¹. There's anecdotal evidence that if a Leaf pack gets extremely hot (12 bars), it can take hours to recover – effectively you're stuck at low power until it naturally cools or you stop driving.

- **Chevy Bolt (GM)**: The Bolt EV has liquid cooling and generally keeps the battery under ~50 °C. If it overheats (for example, multiple DC fast charges in a row), the car will limit charging current significantly (early Bolts would slow down fast charging if the battery got too warm) and might reduce drive power if it ever came to that (though in practice, Bolts seldom hit power limit due to overheat in reviews). The Bolt's BMS will throw a warning message if the battery is too hot and it may disable fast charging until it cools.

- **BMW/Thermal Management Standards**: Some German OEMs design for very robust thermal control – e.g. BMW had an SAE paper noting they keep cell temps below 55 °C at all times through cooling. But if cooling fails, the car would likely go into a controlled shutdown to avoid battery damage rather than let temps skyrocket.

Additionally, there are industry standards and best practices: e.g. ISO 6469-1 and -3 (and similar SAE documents) require that an EV must alert the driver of an over-temperature and ultimately isolate the battery if it's in an unsafe state. Also, functional safety standards (ISO 26262) classify an overheat leading to fire as a hazard to be mitigated – so multiple redundant measures (sensors, software limits, perhaps even thermal fuses) are implemented.

For our purposes, we can summarize: **Modern BMS detect thermal issues within seconds and respond within seconds**, using multi-stage power derating before resorting to disconnect or shutdown. Fully shutting off power (contactor opening) is usually a last resort because it means the vehicle would lose propulsion suddenly – instead BMS tries to limp the vehicle while protecting the battery. This could involve dropping power to 0% (effectively "pull over now") if needed, but ideally the progression is smooth enough to prompt the driver to take action (like find a safe spot to stop) without outright stranding them instantaneously.

### Duration of Thermal Mitigation Modes

How long a car stays in a reduced-power thermal protection mode depends on cooldown, as noted. There isn't a fixed "timeout" – it's driven by temperature. Some vehicles might also log a fault code that requires a manual reset if an extreme over-temp occurred (for safety checks), but generally once temps are back in range, the BMS will restore normal operation either automatically or after an ignition cycle.

In fleet/telematics data, you'd see the battery temperature parameter come down and the available power ramp back up correspondingly. In our simulation or monitoring system, we can model that after an emergency shutdown at 60 °C, the system might need, say, 5 minutes to cool below 55 °C before allowing restart, etc., to mimic reality.

## 4. Real-World Thermal Event Frequency and Critical Scenarios

### Frequency of Thermal Incidents in EV Fleets

High-profile EV battery fires make news, but statistically they are quite rare. Data from the U.S. National Transportation Safety Board (NTSB) indicates on the order of **25 fires per 100,000 EVs**³⁰, which is actually much lower than the rate for conventional vehicles (for gasoline cars it's about 1,500 per 100k, and hybrids ~3,500 per 100k)³⁰. In other words, only around **0.025% of EVs have a fire incident**, versus a few percent of gasoline cars. This suggests that full-blown thermal runaway events (battery fires) are extremely infrequent.

They typically occur due to manufacturing defects (e.g. the Chevy Bolt recall involved ~15 battery fires traced to internal cell flaws out of tens of thousands of vehicles), severe crashes causing internal damage, or improper modifications/charging. However, **less catastrophic thermal events – such as overheating without fire – are more common** and relevant for a monitoring system.

For example, fleet vehicles in hot climates might regularly push the battery to the edge of safe temperature if fast-charged frequently. Anecdotally, rideshare or taxi drivers with first-gen Nissan Leafs in Arizona experienced "turtle mode" after multiple rapid charges in a day¹ ²⁹. Tesla owners doing back-to-back Supercharging on road trips might notice the second or third session is throttled due to battery warmth (Tesla's BMS will taper charge current to manage pack temperature).

High-performance driving is another scenario: EV track days are still relatively rare, but as seen, a performance EV can hit thermal limits after a few hard laps¹⁴ ¹⁵. These instances are not everyday commuting, but in the context of fleets or repeated abuse, they become more likely. For a **"battery health monitoring system", it's crucial to catch those moderate thermal events** (overheating that triggers BMS intervention) because they can impact battery longevity and indicate stress, even if they don't result in fires.

### Most Critical Scenarios to Detect

Based on real-world data, the scenarios of greatest concern for thermal issues are:

1. **DC Fast Charging in Hot Conditions**: This is arguably the top use-case to monitor (and you identified it as #1). When an EV is fast-charged in a hot climate (e.g. Phoenix in summer), the battery is heat-stressed both from environment and from charging current. A monitoring system should watch for rapid temperature rise during fast charge and whether the pack approaches critical thresholds. In practice, vehicles manage this by throttling charge – e.g. the "Rapidgate" software update on Nissan Leaf deliberately slows the charging when the battery is too hot¹². But an external monitor can provide additional warnings or predictive alerts (e.g. "Battery temperature high; charging will slow down" or "Consider cooling before next charge").

2. **High Discharge Situations (Performance Driving or Towing)**: Track days, aggressive mountain climbs, towing heavy loads up long grades – these push discharge currents high for sustained periods, generating significant I²R heat. Most EVs will handle it for some time (thanks to cooling), but after a threshold, they'll start power-limiting. These events are important to detect because the driver might need to back off to avoid hitting limp mode. For example, a Tesla Model S at the Nürburgring will eventually overheat the powertrain; a monitoring tool could warn "battery temp approaching limit, reduce pace." For fleet vehicles, think about a delivery van climbing hills in summer – same idea.

3. **Repeated Fast Charge / High Cycle Frequency (Fleet/Rideshare)**: Fleet vehicles that are used nearly continuously (like ride-share EVs, delivery vans, etc.) often have many charge/discharge cycles per day. Even if each individual cycle is within safe limits, the cumulative heat can raise the baseline battery temperature. The Leaf forum example shows a driver on a road trip: after long driving and two fast-charges, the battery was in the red zone¹ ²⁹. A monitoring system for a fleet can flag if a vehicle's battery temp is not getting adequate cooldown between runs.

4. **Cooling System Failures or Degradation**: This is a bit harder to directly detect, but if, say, a coolant pump stops or a radiator is blocked, the battery could begin overheating even under moderate load. The system should catch anomalous heating (e.g. "why is the pack heating up faster than usual for a given current?"). This could prevent a dangerous situation by prompting maintenance. Real-world, there have been occasional service bulletins – e.g. some Ford Mach-E owners had a software bug that disabled battery cooling, leading to overheat warnings; the car's built-in systems caught it, but an external monitor could as well by noticing unusual temp rises.

5. **Thermal Runaway Initiation**: Although rare, this is the most critical to catch early. Signs might include an unexpected rapid localized temperature spike or voltage drop in one module (as a failing cell heats up and loses capacity). Early detection here is measured in seconds, but if possible, it could trigger interventions (like sending an alert to get out of the vehicle, or even triggering fire suppression if available). In fleet or energy storage systems, thermal runaway monitoring is a hot research topic (sensors for off-gas detection, etc.). For our EV monitoring, focusing on temperature sensors, we'd key into any one sensor shooting up faster than physically plausible under normal conditions.

6. **Extreme Ambient Scenarios**: Examples include vehicles parked in the sun (cabin and battery getting hot-soaked) then immediately driven hard or charged. Or conversely, a vehicle in extremely cold weather where heating is aggressive (less of a "overheat" issue, but worth monitoring cells for uniformity to avoid cold-induced damage – not the focus here though). Hot ambient combined with high battery SOC can create a condition where there's little thermal buffer.

### Triggers of True Thermal Emergencies (fires) in Practice

Actual thermal runaway events in the field have mostly been due to **internal cell defects or damage**. For example:

- **Manufacturing defects**: The Chevrolet Bolt EV recall (2017–2019 models) was because a rare manufacturing flaw in some LG Chem cells could lead to an internal short, causing fires during charging. These happened usually when the car was charging or at high SOC, and they were not related to use-case stress; they were essentially random failures. Monitoring-wise, one might see a sudden temperature jump in one module.

- **Overcharging/charging faults**: While EV BMS are designed to prevent overcharge, in accidents or improper repairs, if a battery is charged beyond its limits, it can fail. This is more a concern in lab or DIY scenarios (or something like a damaged charge controller).

- **Severe crashes**: A high-speed crash can crush cells and start a fire. The "thermal emergency" here is clearly accident-triggered and outside normal operation – but interestingly, the time from crash to fire can sometimes be minutes, which is why first responders now monitor crashed EVs closely. Not directly relevant to our monitoring system when driving normally, but a factor in overall safety frequency stats.

- **Thermal propagation from an external fire**: If an EV is in a fire (say a garage fire), the battery can of course heat up and go into runaway. Again not an operational scenario, but contributes to statistics.

- **Edge-case abuses**: e.g. track driving a car with a disabled thermal protection (some enthusiasts hacking limits) – this is not common, but theoretically if someone bypassed BMS limits, they could drive a battery to destruction. We assume normal BMS stays in place.

The common thread is that **everyday usage rarely triggers a full-blown thermal emergency thanks to BMS intervention**. Instead, what's common are incidents of overheating that are managed by the BMS. Those are precisely the events a health monitoring system should log and analyze: e.g. how often is this vehicle hitting temperature warnings? Is the cooling system performing adequately? Are there patterns (like "Vehicle X tends to overheat on fast charge more than others – maybe its cooling is degraded or its battery has higher resistance")? These kinds of analytics can be gold for fleet maintenance and for validating our model.

### Prioritizing Monitoring Focus

Given the above, our monitoring system should prioritize:

- **Tracking max battery temperature and rise rates** during fast charge in hot ambient (flag if approaching limits or if rise is faster than normal profile).
- **Monitoring during high discharge events** (heavy acceleration, long hill climbs, track use) – possibly integrate vehicle speed or power output info to correlate when high temps occur.
- **Keeping an eye on temperature differentials between modules** (a single module getting much hotter could signal an internal problem).
- **Logging frequency of thermal throttling events**. If a fleet car hits thermal limiting once a year, that's fine; if it's doing it daily, that's an issue to address (whether through hardware upgrades or operational changes).
- **Considering ambient context**: e.g. in extremely hot weather, maybe send pre-emptive advice ("Battery is hot – consider a brief cool-down drive or parking in shade before the next charge").

In real-world fleet data, the **most critical scenario to catch early is thermal runaway** (for safety), but as mentioned it's very rare. The **most frequently encountered critical scenario is overheating leading to power limitation** (for reliability/availability). Both are important: one for safety, one for performance and longevity.

To answer the question succinctly: **Thermal runaway events are exceedingly uncommon per vehicle**, whereas **moderate thermal stress events (overheating without fire) are more common in specific use cases** (fast charging in heat, track use, etc.). Our system should be tuned to detect all of these – from the subtle signs of a failing cell to the broad trend of a vehicle that runs hot often – to ensure comprehensive battery health monitoring.

## 5. Model Calibration and Validation Considerations

### Heat Generation Rates (I²R and Charging Inefficiency)

Our model assumes heat generation from ohmic losses (I²R) plus a 5% inefficiency during charging (to account for heat from chemical inefficiency). These are reasonable first-order approximations. For validation: **Is 0.2 Ω and 250 A (discharge) realistic?** Probably not for a Tesla Model 3 pack under normal conditions. A real 82 kWh pack with ~400 V nominal likely has an internal resistance on the order of milliohms per cell; even at the pack level, maybe ~50–100 mΩ (0.05–0.1 Ω) is more typical when warm¹⁵. We artificially used 0.2 Ω "for extreme conditions demo," which quadruples the heating. This was useful to stress the system, but it overshoots realism.

In extreme fast charging, internal resistance actually drops due to elevated temperature and high SOC (until very full). So if anything, 0.2 Ω is conservative in that it exaggerates heat; a real pack might generate ~1/4 the heat at the same current. However, internal resistance can increase with cold temperatures or an aged battery. If we wanted a realistic worst-case, perhaps we consider a highly aged battery with higher resistance, or a segment of the pack that's more resistive. But for a healthy pack, 0.2 Ω is high.

We should verify our I²R heat against known values: e.g. a Model 3 at 250 A (that's roughly a ~3C discharge rate at ~80 kW output) likely would produce on the order of **a few kW of heat**, not 12.5 kW. Indeed, if R were 0.05 Ω, I²R = 0.05 * 62,500 ≈ 3.1 kW heat at 250 A, which sounds plausible. Our model used 12.5 kW, which is significantly above plausible for continuous operation (the car would almost certainly throttle or trip if 12.5 kW of heat were pouring into the pack continuously – that's like running four big space heaters inside the battery!).

So, to calibrate, we might consider using a more realistic pack resistance (0.05 Ω baseline, maybe 0.1 Ω for a stressed scenario) and see if our thermal timelines become more reasonable.

**Regarding the 5% charging loss**: Fast-charging a lithium battery is indeed not 100% efficient – some energy goes into heat due to internal resistance and entropy change. At high SOC and high C-rate, charging efficiency can drop into the 90-95% range, meaning 5–10% of energy is heat²⁵ ¹¹. So 5% as a fixed number is a simplification, but a fair one for a rough model. It might be a bit low at peak charge power (maybe 8% heat at the very peak current, then less at lower currents). But overall, it's in the right ballpark.

We should ensure the I²R term isn't double-counting with that inefficiency though – in charging, the dominant heat source is still I²R, plus some entropic heat if charging at low temps. So one could argue the 5% is effectively another way to say "internal resistance causes about a 5% loss at that current." It might be cleaner to just stick to I²R and adjust R to simulate the inefficiency. Regardless, our heat generation formula seems qualitatively fine, but quantitatively we should validate it with known data.

### Effective Thermal Mass (120 kg vs 400 kg)

We assumed the pack's thermal mass is 120 kg (with c≈1000 J/kg·K, so 120,000 J per °C) even though the physical pack mass is ~400 kg. This was likely to reflect that not all components heat up uniformly or as quickly – perhaps just the cell mass or a portion of it is considered in the rapid thermal response. **Is 120 kg reasonable?**

The Tesla Model 3 pack's cells themselves weigh on the order of ~300–350 kg (the rest being casing, coolant, etc.). If only part of the pack is heating intensely (e.g. just one module), using a smaller effective mass could make sense. But in our simulation, we applied it to the whole pack temperature – which implicitly assumes the whole pack acts like a 120 kg object. That might be too low, causing an artificially fast temp rise.

In reality, heat will slowly diffuse to the pack structure, cooling plates, etc., effectively increasing the thermal mass over time. So our model's 120 kg might be underestimating heat capacity by a factor of ~2–3 for the whole pack. If we increased the thermal mass in the model, we'd see slower temperature changes, which would be more "forgiving" – perhaps more realistic for a large pack.

On the other hand, if we are modeling a scenario like "cooling failure in one module," a smaller thermal mass (that of one module) could be appropriate. To validate, we could compare with empirical data: e.g. a 3 kW heating on a ~82 kWh pack – how fast does it warm up in reality? If a car dissipates 3 kW in the pack, that's like driving hard. If the pack (let's say ~300 kg effective mass) absorbs 3 kW, that's 3,000 J/s. Over 60 seconds, 180,000 J, divided by (300,000 J/°C) = 0.6 °C rise per minute. Over 10 minutes, ~6 °C rise. That feels plausible – a pack might go from 30 to 36 °C after a hard 10-min drive if no cooling.

Our model with 120 kg mass would predict 300,000 J raising it 2.5x more (because less mass) -> ~1.5 °C per minute in that scenario. So indeed, we may be overshooting the dynamics. Therefore, adjusting the thermal mass upward could make our simulation's timescales more realistic. Perhaps we consider using the full ~300–400 kg for slow events and reserve a smaller mass for localized fast events. At minimum, we should acknowledge this simplification when presenting results.

### Cooling Rate Variations (Speed, Fans, etc.)

Our current model uses Newton's cooling law with a coefficient (hA) of 0.001 in normal cases, reduced to 0.0001 in the extreme test (to simulate greatly diminished cooling). In reality, the cooling power is highly variable:

- If the car is at speed (wind blowing over radiators or battery casing), cooling is much more effective. Also, many EVs route the AC chiller to the battery under high cooling demand, which can dramatically increase heat removal (coolant can be chilled below ambient).
- If the car is stopped or the cooling system is off, cooling is minimal – essentially just passive thermal radiation/convection.
- If the battery cooling system fails completely, then aside from some thermal conduction to the chassis and whatever passive air flow, there's very little cooling – that's close to our 0.0001 scenario.
- If the system is working hard, our coefficient could be an order of magnitude higher than normal.

In other words, our approach of using different coefficients is on the right track. We should refine it by tying it to vehicle state:
- During Phase 1 (discharge), presumably the car might have been moving (if this simulates track driving or highway pull). If moving at high speed, cooling could be better than at idle. However, if we assume an extreme case of no cooling (maybe fans broke), then okay.
- During idle (Phase 2), if fans are on, the pack could cool somewhat; if fans are off, it might actually retain heat.
- During Phase 3 (charge), typically the cooling system would work the hardest (because charging in 40 °C ambient is tough). Tesla, for example, will run the AC compressor at full tilt while Supercharging in hot weather. So even in 40 °C ambient, they manage to keep battery from skyrocketing (though maybe hovering around 50–55 °C). If we disabled cooling in our model, we got the runaway rise to shutdown. It would be interesting to simulate Phase 3 with a moderate cooling coefficient (not as high as normal, because ambient 40 °C reduces deltaT, but some cooling) to see a more realistic outcome – likely the battery might stabilize in the 50s °C instead of hitting 60 so fast.

To validate cooling, we can consult specs: The **heat rejection capacity** of EV cooling systems can be tens of kW. If a battery is generating 10 kW of heat, a well-designed cooling could remove ~5–10 kW of that (depending on conditions). Our simple Newtonian model might not capture saturation, but by tweaking the coefficient we can approximate. For example, at a 10 °C delta (battery vs ambient) and hA=0.001, heat removal = 0.001 * 10 = 0.01 (in whatever units our model uses relative to heat capacity). Hard to directly equate without units, but qualitatively, yes.

**The key point**: Yes, cooling rates should vary with conditions. A refined model might have:
- hA as a function of vehicle speed and whether the AC is active.
- Possibly separate modes: "parked passive", "moving passive", "active cooling on".

We already manually did this by an order of magnitude change. We might consider that at highway speeds with fans on, an even higher coefficient than 0.001 could be used. Conversely, 0.0001 was an extreme "no cooling at all" (which matched our extreme test narrative of a cooling failure).

As an example of how vehicles manage cooling dynamically: VW ID.3 (from earlier) turns on its battery cooling above 32.5 °C automatically²⁴. Many cars will modulate coolant pump speed based on temperature. So in our model, we could emulate that by switching to a higher cooling coefficient once T > some threshold (like a thermostat).

**Validation approach**: If possible, compare model cooling with real cooldown data. E.g., a Tesla battery cooling from 50 °C to 40 °C might take ~10 minutes with fans on in moderate ambient. Does our model replicate that with a given coefficient? That could calibrate hA. If not, at least ensure we cite sources indicating that active cooling significantly boosts heat rejection so our approach to adjust the coefficient is justified. (We do have a source: water cooling is ~3500x more effective than air by volume, etc., but that CEJN article basically said "needs liquid cooling, 270 °C if not"¹³. We can cite the general need for liquid cooling at high charge rates.)

Overall, it would be wise to present that our model's cooling constant is a tunable parameter and that in reality it correlates with factors like coolant flow rate and air speed. We already showed we know this by varying it; now in documentation we confirm that's intentional and aligned with real vehicle behavior.

### Real-World Data for Model Validation

We should back up our model's behaviors with any real data points available:

- **The timeline from our extreme test**: got to 50 °C by t=31 s, 60 °C by t=113 s under heavy 250 A discharge + 200 A charge conditions with poor cooling. Does any vehicle data show how fast an uncontrolled thermal event might reach those temps? Likely not publicly (because OEMs avoid uncontrolled conditions). But we did reason it's faster than normal. We might validate pieces: e.g. how fast does a Leaf heat up under 125 A CHAdeMO charging? Some LeafSpy users have reported maybe ~1–2 °C increase per 5 minutes when starting in moderate range, which is far slower than our scenario. But the Leaf also limits current as it heats.

- **We can validate the "normal scenario" separately**: say a Model 3 Supercharging from 10% to 80% on a 25 °C day – the pack might start ~30 °C and end ~50 °C over ~20 minutes. That's 20 °C rise in 1200 s (0.016 °C/s). Our extreme scenario was ~10 °C rise in 82 s (0.12 °C/s) – nearly an order of magnitude higher rate. So clearly that was beyond typical.

Using such comparisons, we can adjust parameters for a "normal hot climate fast charge" scenario in our simulation to demonstrate it aligns with known behavior (no shutdown in 82 s, rather maybe a steady state or slow approach to ~55 °C over several minutes).

### Aligning with Automotive Engineering Reality

To ensure credibility, we want our model to produce results that an automotive engineer nods at and says "that seems about right." This means calibrating not just absolute thresholds but the dynamic behavior. We've discussed adjusting internal resistance, thermal mass, and cooling to achieve that. We should also document any assumptions, such as "we assumed uniform pack temperature," whereas in reality there will be gradients (cells in the center of a module may run hotter, etc.). Uniform temperature is a common simplification but can be a source of error when comparing to reality (where one hot sensor can trigger limits even if average pack temp is lower). In future, we could incorporate a simple multi-node thermal model (e.g. core vs surface temps).

Finally, we should leverage any case studies or test data for validation. One valuable source could be academic papers that measured thermal event timescales. For instance, an academic study might say "under a 3C discharge, cell temperature rose to 60 °C in X minutes" – we should see if our model would do similar. The ASME paper we referenced noted uneven heating and that cells degrade faster in the middle of a pack³¹, which hints at internal pack thermal gradients – again implying our single-mass model is a simplification.

In summary, to validate and calibrate:
- Use realistic internal resistance values for given C-rates (adjust our R down from 0.2 for nominal scenarios).
- Use a larger effective thermal mass for whole-pack scenarios (closer to actual pack mass or a fraction of it that seems reasonable).
- Use dynamic cooling rates reflecting actual thermal management strategies (high when fans/pumps on, near-zero if off).
- Compare outcomes (times to reach 50, 55, 60 °C) against any known real-world observations, and iteratively adjust parameters.
- Document the comparison: e.g., "Our model predicts ~10 minutes to go from 30→50 °C under X condition, which matches well with anecdotal reports from EV Y on a track," or conversely adjust if it doesn't match.

On the charging inefficiency side, 5% is okay, but note that if we already have I²R capturing most losses, the 5% might be double-counting a bit. One way to refine is to incorporate the battery's entropic heat term, which can cause batteries to heat or cool slightly during charge depending on SoC. At high SoC, charging actually causes additional heat because the reaction is endothermic in discharge and exothermic in charge for many chemistries near full. But such detail may be beyond our scope. 5% flat is a decent approximation for extra heat during fast charge beyond pure ohmic losses.

Lastly, consider LFP vs NCM calibration: If we simulate a Nissan Leaf (LMO/NMC chemistry, passive cooled), we'd use different parameters (lower cooling, perhaps slightly different heat generation since Leaf's pack IR might be higher as it heats in use). If we simulate an LFP pack (say in a Tesla Model 3 LFP version), we might note that its internal resistance might differ and its thermal mass per kWh might differ. But those are fine details; our primary focus is NCM which we've covered.

By incorporating these validation steps, we ensure our simulation outputs "authentic timescales" and behaviors. For instance, after calibration we might conclude: **Gradual overheating (cooling failure) from 25 °C to 60 °C takes ~10–20 minutes in our model under extreme 250 A discharge**, which is more realistic than 82 s, and matches the expectation that even with no cooling a pack has significant thermal inertia. We can then be confident presenting those results as credible.

## References

### Real EV thermal limits and behavior:
- Tesla Model 3 Performance track test (battery ~55 °C normal max, >60 °C triggers power cut)¹⁵ ¹⁷
- Nissan Leaf BMS strategy (progressive power reduction at 10–12 temperature bars ≈ 50–60 °C)²⁰ ²¹

### Optimal and critical battery temperatures:
- Industry guidelines (15–45 °C optimal, >60 °C dangerous)¹⁰ ¹¹

### Thermal runaway propagation times and safety standards:
- Need 5-minute delay, otherwise propagation in seconds without mitigation⁸ ⁷ ⁴

### Real-world case of hot climate fast charging causing battery overheat:
- "Rapidgate"²⁹ ¹²

### EV fire incident statistics:
- EVs ~25 fires per 100k vs gas cars ~1530 per 100k³⁰

### NMC vs LFP thermal stability:
- LFP runs away at higher temp and less violently, but still subject to overheating¹⁹

---

## Sources

¹ ² ³ ¹² ²⁹ Battery temperature gauge in red after fast charging (or a long day of driving)? | My Nissan Leaf Forum  
https://mynissanleaf.com/threads/battery-temperature-gauge-in-red-after-fast-charging-or-a-long-day-of-driving.35796/

⁴ Experiments Completed for Intentional Thermal Runaway on Lithium-Ion Batteries | Fire Safety Research Institute (FSRI), part of ULRI  
https://fsri.org/research-update/experiments-completed-intentional-thermal-runaway-lithium-ion-batteries

⁵ ⁹ It's About Time: The 6 Phases of Thermal Runaway Propagation  
https://www.aerogel.com/resources-library/thermal-runaway-phases-and-preventing-runaway-propagation/

⁶ ⁷ ⁸ Charged EVs | Thermal runaway in EV battery packs: designing a mitigation strategy - Charged EVs  
https://chargedevs.com/newswire/thermal-runaway-in-ev-battery-packs-designing-a-mitigation-strategy/

¹⁰ ¹¹ ²⁵ ²⁷ EV Thermal Management and Sensor Technology Guide for Manufacturers  
https://amphenol-sensors.com/ev-thermal-management-and-sensors-for-manufacturers

¹³ Thermal management for safe and efficient fast-charging of battery electric vehicles on the road | CEJN (US)  
https://www.cejn.com/en-us/articles/thermal-management-for-safe-and-efficient-fast-charging-of-battery-electric-vehicles-on-the-road/

¹⁴ ¹⁵ ¹⁶ ¹⁷ 2024 Tesla Model 3 Performance Can't Handle the Track, Overheats - autoevolution  
https://www.autoevolution.com/news/2024-tesla-model-3-performance-can-t-handle-the-track-overheats-236595.html

¹⁸ LFP vs NMC thermal runaway  
https://www.electrichybridvehicletechnology.com/technical-articles/lfp-vs-nmc-thermal-runaway.html

¹⁹ NMC vs LFP: safety and performance in operation - PowerUp  
https://powerup-technology.com/nmc-vs-lfp-safety-and-performance-in-operation/

²⁰ ²¹ ²⁸ What happens when the battery "overheats"? | My Nissan Leaf Forum  
https://mynissanleaf.com/threads/what-happens-when-the-battery-overheats.34339/

²² ²³ ²⁴ ³¹ Challenges and Innovations of Lithium-Ion Battery Thermal Management Under Extreme Conditions: A Review  
https://ecec.me.psu.edu/Pubs/2023_Liu_JHMT.pdf

²⁶ LiFePO4 Battery BMS: 25 Key Parameters for Smart Management  
https://www.docanpower.com/BLOG-and-FEEDBACKS/lifepo4-battery-bms-25-key-parameters-for-smart-management-in-2025

³⁰ Data Shows EVs are Less of a Fire Risk than Conventional Cars | Office of Environmental and Energy Coordination  
https://www.fairfaxcounty.gov/environment-energy-coordination/climate-matters/EV-less-fire-risk