/** Legend row beneath the map: each verdict as glyph + word + count (mono), plus an optional subject line ("Telehealth video, 96 communities"). */
export interface MapLegendProps {
  counts?: { works?: number; degraded?: number; fails?: number; nodata?: number };
  subject?: string;
}
export function MapLegend(props: MapLegendProps): JSX.Element;
