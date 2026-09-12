/**
 * Inline-SVG map of the NT with one point per community, drawn in the verdict colour and glyph shape (circle, triangle, square, dash). No tiles, no network.
 * @startingPoint section="Screens" subtitle="NT map with 96 verdict points" viewport="360x600"
 */
export interface MapPoint { id: string; name?: string; lon: number; lat: number; verdict: 'works' | 'degraded' | 'fails' | 'nodata' }
export interface NtMapProps {
  points: MapPoint[];
  /** Draws the ink ring and the name label on this point */
  selectedId?: string;
  onSelect?: (point: MapPoint) => void;
  label?: string;
}
export function NtMap(props: NtMapProps): JSX.Element;
