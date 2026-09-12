/** The verdict: glyph + word + colour, always together. The only place chromatic colour appears. */
export interface VerdictBadgeProps {
  /** works ● green · degraded ▲ ochre · fails ■ red · nodata – grey */
  verdict: 'works' | 'degraded' | 'fails' | 'nodata';
}
export function VerdictBadge(props: VerdictBadgeProps): JSX.Element;
