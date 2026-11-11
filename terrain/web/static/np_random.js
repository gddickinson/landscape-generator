// Bit-exact JavaScript port of numpy.random.default_rng(seed): SeedSequence -> PCG64 (XSL-RR 128/64)
// -> Generator.random / uniform / normal (NumPy's 256-layer ziggurat). Same seed, same numbers as NumPy,
// so the terrain noise in the browser matches the Python package. Checked by np_random.test.mjs.
import { KI_DOUBLE, WI_DOUBLE, FI_DOUBLE, ZIGGURAT_NOR_R, ZIGGURAT_NOR_INV_R } from './ziggurat_tables.js';

const M32 = 0x100000000;
const imul = Math.imul;

// --- SeedSequence (numpy/random/bit_generator.pyx) ------------------------------------------------
const INIT_A = 0x43b0d7e5, MULT_A = 0x931e8875, INIT_B = 0x8b51f9dd, MULT_B = 0x58f38ded;
const MIX_MULT_L = 0xca01f9dd, MIX_MULT_R = 0x4973f715;

function intToUint32Array(n) {
  if (!Number.isSafeInteger(n) || n < 0) throw new Error('seed must be a non-negative integer below 2**53');
  if (n === 0) return [0];
  const out = [];
  while (n > 0) { out.push(n % M32 >>> 0); n = Math.floor(n / M32); }
  return out;
}

// Returns n_words uint32 words of seeding state (as SeedSequence(seed).generate_state(n_words)).
export function seedSequenceState(seed, nWords) {
  const entropy = intToUint32Array(seed);
  const pool = new Uint32Array(4);
  let hc = INIT_A;
  const hashmix = v => {
    v = (v ^ hc) >>> 0; hc = imul(hc, MULT_A) >>> 0;
    v = imul(v, hc) >>> 0; return (v ^ (v >>> 16)) >>> 0;
  };
  const mix = (x, y) => { let r = (imul(MIX_MULT_L, x) - imul(MIX_MULT_R, y)) >>> 0; return (r ^ (r >>> 16)) >>> 0; };
  for (let i = 0; i < 4; i++) pool[i] = hashmix(i < entropy.length ? entropy[i] : 0);
  for (let s = 0; s < 4; s++) for (let d = 0; d < 4; d++) if (s !== d) pool[d] = mix(pool[d], hashmix(pool[s]));
  for (let s = 4; s < entropy.length; s++) for (let d = 0; d < 4; d++) pool[d] = mix(pool[d], hashmix(entropy[s]));
  const out = new Uint32Array(nWords);
  let hb = INIT_B;
  for (let i = 0; i < nWords; i++) {
    let v = (pool[i % 4] ^ hb) >>> 0; hb = imul(hb, MULT_B) >>> 0;
    v = imul(v, hb) >>> 0; out[i] = (v ^ (v >>> 16)) >>> 0;
  }
  return out;
}

// --- PCG64: 128-bit LCG held as eight 16-bit limbs (little-endian), products stay exact in doubles --
// Multiplier 0x2360ED051FC65DA44385DF649FCCF645 as 16-bit limbs, least significant first.
const [M0, M1, M2, M3, M4, M5, M6, M7] = [0xf645, 0x9fcc, 0xdf64, 0x4385, 0x5da4, 0x1fc6, 0xed05, 0x2360];

function limbsFromWords(w) { // w: four uint32, least significant first
  const l = new Float64Array(8);
  for (let i = 0; i < 4; i++) { l[2 * i] = w[i] & 0xffff; l[2 * i + 1] = w[i] >>> 16; }
  return l;
}

export class PCG64 {
  constructor(seed) {
    const st = seedSequenceState(seed, 8); // generate_state(4, uint64): uint64 k = st[2k] | st[2k+1] << 32
    // initstate = val[0] << 64 | val[1];  initseq = val[2] << 64 | val[3]
    const initstate = limbsFromWords([st[2], st[3], st[0], st[1]]);
    const initseq = limbsFromWords([st[6], st[7], st[4], st[5]]);
    this.s = new Float64Array(8);
    this.inc = new Float64Array(8);
    let carry = 1; // inc = initseq << 1 | 1
    for (let i = 0; i < 8; i++) { const v = initseq[i] * 2 + carry; this.inc[i] = v & 0xffff; carry = v >>> 16; }
    this.step();
    carry = 0;
    for (let i = 0; i < 8; i++) { const v = this.s[i] + initstate[i] + carry; this.s[i] = v % 65536; carry = v >= 65536 ? 1 : 0; }
    this.step();
    this.hi = 0; this.lo = 0; // last 64-bit output
  }

  step() { // s = s * MULT + inc (mod 2**128), unrolled; every partial sum stays below 2**53
    const s = this.s, inc = this.inc;
    const s0 = s[0], s1 = s[1], s2 = s[2], s3 = s[3], s4 = s[4], s5 = s[5], s6 = s[6], s7 = s[7];
    let a, c;
    a = inc[0] + s0 * M0; c = Math.floor(a / 65536); s[0] = a - c * 65536;
    a = c + inc[1] + s0 * M1 + s1 * M0; c = Math.floor(a / 65536); s[1] = a - c * 65536;
    a = c + inc[2] + s0 * M2 + s1 * M1 + s2 * M0; c = Math.floor(a / 65536); s[2] = a - c * 65536;
    a = c + inc[3] + s0 * M3 + s1 * M2 + s2 * M1 + s3 * M0; c = Math.floor(a / 65536); s[3] = a - c * 65536;
    a = c + inc[4] + s0 * M4 + s1 * M3 + s2 * M2 + s3 * M1 + s4 * M0; c = Math.floor(a / 65536); s[4] = a - c * 65536;
    a = c + inc[5] + s0 * M5 + s1 * M4 + s2 * M3 + s3 * M2 + s4 * M1 + s5 * M0; c = Math.floor(a / 65536); s[5] = a - c * 65536;
    a = c + inc[6] + s0 * M6 + s1 * M5 + s2 * M4 + s3 * M3 + s4 * M2 + s5 * M1 + s6 * M0;
    c = Math.floor(a / 65536); s[6] = a - c * 65536;
    a = c + inc[7] + s0 * M7 + s1 * M6 + s2 * M5 + s3 * M4 + s4 * M3 + s5 * M2 + s6 * M1 + s7 * M0; s[7] = a % 65536;
  }

  // Advance and set this.hi / this.lo to the 64-bit XSL-RR output (as unsigned 32-bit halves).
  next() {
    this.step();
    const s = this.s;
    const xlo = ((s[0] + s[1] * 65536) ^ (s[4] + s[5] * 65536)) >>> 0;
    const xhi = ((s[2] + s[3] * 65536) ^ (s[6] + s[7] * 65536)) >>> 0;
    const rot = s[7] >>> 10; // top 6 bits of the state
    if (rot === 0) { this.hi = xhi; this.lo = xlo; return; }
    let h = xhi, l = xlo, r = rot;
    if (r >= 32) { const t = h; h = l; l = t; r -= 32; }
    if (r === 0) { this.hi = h; this.lo = l; return; }
    this.lo = ((l >>> r) | (h << (32 - r))) >>> 0;
    this.hi = ((h >>> r) | (l << (32 - r))) >>> 0;
  }

  // next_uint64 as a decimal string (BigInt), for tests.
  rawString() { this.next(); return (BigInt(this.hi) << 32n | BigInt(this.lo)).toString(); }

  nextDouble() { this.next(); return (this.hi * 2097152 + (this.lo >>> 11)) * 1.1102230246251565e-16; }
}

// numpy.random.Generator subset used by the terrain package.
export class Generator {
  constructor(seed) { this.bg = new PCG64(seed); }

  random() { return this.bg.nextDouble(); }
  uniform(low, high) { return low + (high - low) * this.bg.nextDouble(); }

  standardNormal() {
    const bg = this.bg;
    for (;;) {
      bg.next();
      const lo = bg.lo, hi = bg.hi;
      const idx = lo & 0xff;
      const rabs = (hi & 0x1fffffff) * 8388608 + (lo >>> 9); // bits 9..60
      let x = rabs * WI_DOUBLE[idx];
      if ((lo >>> 8) & 1) x = -x;
      if (rabs < KI_DOUBLE[idx]) return x;
      if (idx === 0) {
        for (;;) {
          const xx = -ZIGGURAT_NOR_INV_R * Math.log1p(-bg.nextDouble());
          const yy = -Math.log1p(-bg.nextDouble());
          if (yy + yy > xx * xx) return ((lo >>> 17) & 1) ? -(ZIGGURAT_NOR_R + xx) : ZIGGURAT_NOR_R + xx;
        }
      } else if ((FI_DOUBLE[idx - 1] - FI_DOUBLE[idx]) * bg.nextDouble() + FI_DOUBLE[idx] < Math.exp(-0.5 * x * x)) {
        return x;
      }
    }
  }

  normal(loc, scale) { return loc + scale * this.standardNormal(); }

  // Fill a Float64Array with n draws of normal(loc, scale), in NumPy's C order.
  normalArray(n, loc, scale) {
    const out = new Float64Array(n);
    for (let i = 0; i < n; i++) out[i] = loc + scale * this.standardNormal();
    return out;
  }

  randomArray(n) {
    const out = new Float64Array(n);
    for (let i = 0; i < n; i++) out[i] = this.bg.nextDouble();
    return out;
  }
}
