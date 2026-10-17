const NUMERALS = [
  [1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'],
  [100, 'C'], [90, 'XC'], [50, 'L'], [40, 'XL'],
  [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I'],
];

export function toRoman(num) {
  let n = Math.max(1, Math.round(num));
  let out = '';
  for (const [value, symbol] of NUMERALS) {
    while (n >= value) {
      out += symbol;
      n -= value;
    }
  }
  return out;
}
