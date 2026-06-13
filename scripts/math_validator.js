// Math engines to be validated
function calculateCoherence(phi, psi, h) {
  const score = 100 * (1 - h / (psi + 0.1));
  return Math.min(100, Math.max(0, score));
}

function calculateOzbilScore(coherence, h) {
  const score = (coherence / 100) * (1 - h) * 100;
  return Math.min(100, Math.max(0, score));
}

function calculateFisherMetrics(psi, h) {
  const f_q = psi * psi;
  const lambda = 2.0;
  const f_c = f_q * Math.exp(-lambda * h);
  const delta_f = f_q - f_c;
  const crlb = f_c > 0.0001 ? (1 / f_c) : Infinity;
  return { f_q, f_c, delta_f, crlb };
}

function calculateEntropy(phi, psi, h, t_elapsed, deviation) {
  const t = t_elapsed !== undefined ? t_elapsed : 3.0;
  const dev = deviation !== undefined ? deviation : 0.0;
  const GR = 1.61803398875;
  const stateNorm = Math.sqrt(phi * phi + psi * psi + h * h);
  const microCorrection = dev * Math.max(0, 1 - t / 3.0);
  const torusArg = GR + stateNorm * (Math.pow(Math.sin(phi), 2) + Math.pow(Math.cos(psi), 2)) + microCorrection;
  return Math.max(0, h * Math.log(torusArg));
}

function calculateWaveHeight(x, y, t, phi, psi, h, t_elapsed, deviation) {
  const t_el = t_elapsed !== undefined ? t_elapsed : 3.0;
  const dev = deviation !== undefined ? deviation : 0.0;
  const dist = Math.sqrt(x * x + y * y);
  const corr = Math.max(0, 1 - t_el / 3.0);
  const effectivePhi = phi * (1 - corr) + 1.62 * corr;
  const effectivePsi = psi * (1 - corr) + 2.00 * corr;
  const effectiveH = h * (1 - corr) + 0.05 * corr;
  return effectivePsi * Math.cos(dist * effectivePhi - t) * Math.exp(-effectiveH * (x * x + y * y) / 1000);
}

function calculateSymbiosis(phi, psi, h) {
  return (phi * psi) / (1 + h);
}

function calculateSurvivalProbability(phi, psi, h, temp) {
  const coherence = calculateCoherence(phi, psi, h);
  const T_norm = temp / 5800;
  const lambda = 0.5;
  const exponent = - (lambda * h * T_norm) / (1 + psi);
  return coherence * Math.exp(exponent);
}





// SPHY-Wiens Wavelength Peak Calculation
function calculateWiensWavelength(temp, gravity) {
  const b = 2897.7; // Wien's displacement constant in nm K (approx scaled)
  return b / (temp * (1 + gravity));
}

// Map wavelength to basic RGB color profiles
function mapWavelengthToRGB(wl) {
  // wl is in micro-units/scaled nm (approx 0.05 to 3.0 scale corresponding to visible region)
  // Low wl => blue/violet
  // Mid wl => green/white
  // High wl => red/orange
  if (wl < 0.3) {
    return { r: 157, g: 78, b: 221 }; // violet
  } else if (wl < 0.8) {
    return { r: 0, g: 229, b: 255 };  // cyan
  } else if (wl < 1.8) {
    return { r: 57, g: 255, b: 14 };  // green
  } else {
    return { r: 255, g: 64, b: 129 }; // red/pink
  }
}

// Test runner
const suites = [];
function test(name, fn) {
  suites.push({ name, fn });
}

test('Coherence Score limits and boundary checks', () => {
  const score1 = calculateCoherence(1.0, 1.0, 0.0);
  if (score1 !== 100) throw new Error(`Expected 100 with zero H, got ${score1}`);

  const score2 = calculateCoherence(1.0, 0.5, 2.0);
  if (score2 !== 0) throw new Error(`Expected 0 with high H, got ${score2}`);

  const score3 = calculateCoherence(1.0, 0.0, 0.1);
  if (Math.abs(score3 - 0) > 0.0001) throw new Error(`Expected 0 with psi=0, h=0.1, got ${score3}`);
});

test('Entropy calculation logic', () => {
  // Under SPHY-SACKUR_TETRODE, entropy is strictly non-negative & NaN-immune
  const entropyZero = calculateEntropy(0, 0, 0, 0, 0);
  if (entropyZero !== 0) throw new Error(`Expected 0 entropy with H=0, got ${entropyZero}`);

  // Validate Golden Ratio and torus phase-space confinement boundary
  const entropyBound = calculateEntropy(0, 0, 0.5, 0, 0); // phi=0, psi=0, h=0.5
  const expectedBound = 0.5 * Math.log(1.61803398875 + 0.5 * (0 + 1));
  if (Math.abs(entropyBound - expectedBound) > 0.0001) {
    throw new Error(`Expected ${expectedBound}, got ${entropyBound}`);
  }

});

test('SPHY-SACKUR_TETRODE 3s Cybernetic stabilization decay', () => {
  const dev = 1.0;
  // At t = 0, correction factor is 1.0
  const entropyStart = calculateEntropy(1.0, 1.0, 0.5, 0.0, dev);
  // At t >= 3.0s, correction factor is 0.0
  const entropyEnd = calculateEntropy(1.0, 1.0, 0.5, 3.0, dev);
  
  if (entropyStart <= entropyEnd) {
    throw new Error(`Expected initial entropy to be larger due to microcorrection`);
  }
});


test('Symbiosis Index formula correctness', () => {
  const symbiosis1 = calculateSymbiosis(2.0, 3.0, 1.0);
  if (symbiosis1 !== 3.0) throw new Error(`Expected 3.0, got ${symbiosis1}`);
});

test('Wave height calculations', () => {
  const height1 = calculateWaveHeight(0, 0, 0, 1.0, 1.0, 0.0);
  if (Math.abs(height1 - 1.0) > 0.0001) throw new Error(`Expected wave peak at origin, got ${height1}`);
});

test('SPHY-Wiens Wavelength mapping boundary calculations', () => {
  // T = 1000, G = 0 => wl = 2897.7 / 1000 = 2.8977
  const wl1 = calculateWiensWavelength(1000, 0);
  if (Math.abs(wl1 - 2.8977) > 0.0001) throw new Error(`Expected 2.8977, got ${wl1}`);

  // T = 2000, G = 1 => wl = 2897.7 / (2000 * 2) = 2897.7 / 4000 = 0.7244
  const wl2 = calculateWiensWavelength(2000, 1);
  if (Math.abs(wl2 - 0.724425) > 0.0001) throw new Error(`Expected 0.724425, got ${wl2}`);
});

test('Planckian locus color classification', () => {
  const color1 = mapWavelengthToRGB(0.2); // Violet
  if (color1.r !== 157 || color1.b !== 221) throw new Error('Expected violet RGB tuple');

  const color2 = mapWavelengthToRGB(2.5); // Red/pink
  if (color2.r !== 255 || color2.g !== 64) throw new Error('Expected red/pink RGB tuple');
});

test('Simulated handshake SHA-256 hash format verification', () => {
  const hashRegex = /^SHA256: [a-f0-9]{64}$/;
  const mockHash = 'SHA256: 8a5d3f82b71c0fe9f45d2e2938ab47120aefbca9283e10fa654cd7ef02e48fa9';
  if (!hashRegex.test(mockHash)) {
    throw new Error('Failed to validate mock SHA-256 hash format');
  }
});

function parseNullProxyCommand(msg) {
  const clean = msg.toLowerCase().trim();
  if (clean.includes('sweep') || clean.includes('temperature') || clean.includes('temp')) {
    return 'SWEEP_TEMP';
  }
  if (clean.includes('stabilize') || clean.includes('lock')) {
    return 'STABILIZE';
  }
  if (clean.includes('disable') && (clean.includes('noise') || clean.includes('stochastic') || clean.includes('geant4'))) {
    return 'DISABLE_NOISE';
  }
  if (clean.includes('enable') || clean.includes('stochastic') || clean.includes('noise') || clean.includes('geant4') || clean.includes('casino')) {
    return 'ENABLE_NOISE';
  }
  return 'GENERIC_CHAT';
}

function extractTemperature(msg) {
  const clean = msg.toLowerCase().trim();
  const match = clean.match(/(\d+)/);
  if (match) {
    const val = parseInt(match[1]);
    if (val >= 1000 && val <= 12000) {
      return val;
    }
  }
  return 9000; // default
}

test('NullProxy Chat routing and command parsing', () => {
  const cmd1 = parseNullProxyCommand('Please sweep temperature to 9000 K');
  if (cmd1 !== 'SWEEP_TEMP') throw new Error(`Expected SWEEP_TEMP command, got ${cmd1}`);

  const cmd2 = parseNullProxyCommand('Lock parameter resonance');
  if (cmd2 !== 'STABILIZE') throw new Error(`Expected STABILIZE command, got ${cmd2}`);

  const cmd3 = parseNullProxyCommand('Who are you, Raziel?');
  if (cmd3 !== 'GENERIC_CHAT') throw new Error(`Expected GENERIC_CHAT command, got ${cmd3}`);
});

test('NullProxy temperature extraction helper', () => {
  const t1 = extractTemperature('sweep to 4500 K');
  if (t1 !== 4500) throw new Error(`Expected 4500, got ${t1}`);

  const t2 = extractTemperature('sweep to high heat');
  if (t2 !== 9000) throw new Error(`Expected default 9000, got ${t2}`);

  const t3 = extractTemperature('sweep to 15000 K (out of range)');
  if (t3 !== 9000) throw new Error(`Expected default 9000 due to bounds, got ${t3}`);
});

test('NullProxy SPHY vs GEANT4 stochastic noise commands', () => {
  const cmd1 = parseNullProxyCommand('disable stochastic noise');
  if (cmd1 !== 'DISABLE_NOISE') throw new Error(`Expected DISABLE_NOISE, got ${cmd1}`);

  const cmd2 = parseNullProxyCommand('enable geant4 Monte Carlo simulation');
  if (cmd2 !== 'ENABLE_NOISE') throw new Error(`Expected ENABLE_NOISE, got ${cmd2}`);

  const cmd3 = parseNullProxyCommand('tell me about geant4 stochastic noise');
  if (cmd3 !== 'ENABLE_NOISE') throw new Error(`Expected ENABLE_NOISE, got ${cmd3}`);
});

function generateCSV(data) {
  if (!data || data.length === 0) return '';
  const headers = Object.keys(data[0]);
  return [
    headers.join(','),
    ...data.map(row => headers.map(h => row[h]).join(','))
  ].join('\n');
}

test('DASN Domain-Adaptive Logic boundary states', () => {
  // Kinetic Mode (DASN) alpha = 0.10
  const alpha_kinetic = 0.10;
  const z_score = 10.0;
  const h_kinetic = 1 - Math.exp(-alpha_kinetic * z_score);
  
  // Electrochemical Mode (DASN) alpha = 0.20
  const alpha_electro = 0.20;
  const h_electro = 1 - Math.exp(-alpha_electro * z_score);
  
  if (h_electro <= h_kinetic) {
    throw new Error('Electrochemical mode should have higher disruption sensitivity for the same Z-score');
  }
});

test('CSV Telemetry Export integrity and format', () => {
  const mockData = [
    { cycle: 1, Omega: 98.5, H: 0.02 },
    { cycle: 2, Omega: 97.2, H: 0.04 }
  ];
  const csv = generateCSV(mockData);
  const lines = csv.split('\n');
  
  if (lines[0] !== 'cycle,Omega,H') throw new Error(`Invalid CSV headers: ${lines[0]}`);
  if (lines[1] !== '1,98.5,0.02') throw new Error(`Invalid CSV data row 1: ${lines[1]}`);
});

test('Quantum Immortality Branching Survival Probability', () => {
  // With H = 0 (no disruption), survival must be 100%
  const p1 = calculateSurvivalProbability(1.62, 2.0, 0.0, 5800);
  if (Math.abs(p1 - 100) > 0.0001) {
    throw new Error(`Expected 100% survival with H=0, got ${p1}`);
  }

  // With non-zero disruption, higher temp decreases survival
  const p2 = calculateSurvivalProbability(1.62, 2.0, 0.4, 5800);
  const p3 = calculateSurvivalProbability(1.62, 2.0, 0.4, 10000);
  if (p3 >= p2) {
    throw new Error(`Expected higher temperature to decrease survival probability: p3(${p3}) should be < p2(${p2})`);
  }

  // Higher coherence amplitude (Psi) must increase/shield survival probability
  const p4 = calculateSurvivalProbability(1.62, 0.5, 0.4, 5800);
  const p5 = calculateSurvivalProbability(1.62, 2.5, 0.4, 5800);
  if (p5 <= p4) {
    throw new Error(`Expected higher psi to shield and increase survival: p5(${p5}) should be > p4(${p4})`);
  }
});

test('Halil Özbil Dynamic Fisher Geometry Stress Test', () => {
  const phi = 1.62;
  const psi = 2.00;
  
  // Baseline state H = 0.1
  const h1 = 0.1;
  const metrics1 = calculateFisherMetrics(psi, h1);
  const coh1 = calculateCoherence(phi, psi, h1);
  const omega1 = calculateOzbilScore(coh1, h1);
  
  // Stressed state H = 0.6
  const h2 = 0.6;
  const metrics2 = calculateFisherMetrics(psi, h2);
  const coh2 = calculateCoherence(phi, psi, h2);
  const omega2 = calculateOzbilScore(coh2, h2);
  
  // 1. F_Q should remain the encoded reference limit
  if (metrics1.f_q !== metrics2.f_q) throw new Error("F_Q should remain constant when H changes.");
  
  // 2. F_C should decrease
  if (metrics2.f_c >= metrics1.f_c) throw new Error("F_C should decrease as H increases.");
  
  // 3. ΔF should increase
  if (metrics2.delta_f <= metrics1.delta_f) throw new Error("ΔF should increase as H increases.");
  
  // 4. CRLB should expand
  if (metrics2.crlb <= metrics1.crlb) throw new Error("CRLB should expand (increase) as H increases.");
  
  // 5. Ω should decrease consistently
  if (omega2 >= omega1) throw new Error("Ω should decrease consistently as H increases.");
});

test('Halil Özbil Validation 1: Monte Carlo Perturbation Stability', () => {
  const base_psi = 2.0;
  const h = 0.3;
  let sum_fc = 0;
  const iterations = 1000;
  
  for (let i = 0; i < iterations; i++) {
    // Inject +/- 5% stochastic noise into the wave amplitude
    const noisy_psi = base_psi * (1 + (Math.random() - 0.5) * 0.1);
    const metrics = calculateFisherMetrics(noisy_psi, h);
    sum_fc += metrics.f_c;
  }
  
  const avg_fc = sum_fc / iterations;
  const expected_fc = calculateFisherMetrics(base_psi, h).f_c;
  
  // The average of the Monte Carlo perturbations should converge to the theoretical center
  if (Math.abs(avg_fc - expected_fc) / expected_fc > 0.05) {
    throw new Error(`Monte Carlo average F_C (${avg_fc}) drifted too far from expected (${expected_fc})`);
  }
});

test('Halil Özbil Validation 2: Randomized H(t) Evolution tracking', () => {
  const phi = 1.62;
  const psi = 2.0;
  let current_h = 0.1;
  let previous_omega = calculateOzbilScore(calculateCoherence(phi, psi, current_h), current_h);
  
  // Simulate 10 time steps of random H walks
  for (let t = 0; t < 10; t++) {
    // Random step bounded between 0.0 and 0.8
    current_h = Math.max(0.0, Math.min(0.8, current_h + (Math.random() - 0.2) * 0.1));
    const current_coh = calculateCoherence(phi, psi, current_h);
    const current_omega = calculateOzbilScore(current_coh, current_h);
    
    // Validate bounds
    if (current_omega < 0 || current_omega > 100) {
      throw new Error(`Omega score breached bounds during H(t) evolution: ${current_omega}`);
    }
    previous_omega = current_omega;
  }
});

test('Halil Özbil Validation 3: Fisher Matrix Sensitivity Analysis', () => {
  const psi = 2.0;
  const h = 0.2;
  const lambda = 2.0;
  
  const metrics1 = calculateFisherMetrics(psi, h);
  const metrics2 = calculateFisherMetrics(psi, h + 0.01);
  
  // Numerical derivative of F_C with respect to H
  const numerical_derivative = (metrics2.f_c - metrics1.f_c) / 0.01;
  // Analytical derivative: d(F_C)/dH = -lambda * F_Q * exp(-lambda * H) = -lambda * F_C
  const analytical_derivative = -lambda * metrics1.f_c;
  
  if (Math.abs(numerical_derivative - analytical_derivative) / Math.abs(analytical_derivative) > 0.05) {
    throw new Error(`Fisher matrix sensitivity failed. Numerical: ${numerical_derivative}, Analytical: ${analytical_derivative}`);
  }
});

// Run
console.log('Running telemetry engine validation suite...');
let passed = 0;
let failed = 0;
for (const s of suites) {
  try {
    s.fn();
    console.log(`[PASS] ${s.name}`);
    passed++;
  } catch (err) {
    console.error(`[FAIL] ${s.name}: ${err.message}`);
    failed++;
  }
}

console.log(`\nTests completed: ${passed} passed, ${failed} failed.`);
process.exit(failed > 0 ? 1 : 0);
