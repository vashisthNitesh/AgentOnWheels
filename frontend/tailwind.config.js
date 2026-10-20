import aowPreset from './src/design/tailwind-preset.js'

// Legacy `brand-*` classes are mapped onto the primary token scale so every
// screen shares one accent colour (previously brand was an unrelated blue with
// missing shades such as 300/400/950, which rendered as no colour at all).
const v = (name) => ({ opacityValue }) =>
  opacityValue !== undefined ? `rgb(var(${name}) / ${opacityValue})` : `rgb(var(${name}))`

const brand = Object.fromEntries(
  [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950].map((s) => [s, v(`--color-primary-${s}`)])
)

export default {
  presets: [aowPreset],
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: { brand },
    },
  },
  plugins: [],
}
