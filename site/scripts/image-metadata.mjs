// Reserve the native SVG aspect ratio before an external image finishes loading.
// These dimensions describe the canvas, not its CSS display size.
export function svgDimensions(svg) {
  const tag = svg.match(/<svg\b[^>]*>/i)?.[0]
  const values = tag?.match(/\bviewBox=["']([^"']+)["']/i)?.[1]
    .trim().split(/[\s,]+/).map(Number)
  if (!values || values.length !== 4 || !values.every(Number.isFinite)) return null
  const [, , width, height] = values
  return width > 0 && height > 0 ? { width, height } : null
}
