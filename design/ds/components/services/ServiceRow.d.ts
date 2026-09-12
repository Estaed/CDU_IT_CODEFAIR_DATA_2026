/** One service present in the community with its verdict badge and reason sentence; tapping expands the source lines and the path rule. */
export interface ServiceSource { label?: string; source?: string; date?: string }
export interface ServiceRowProps {
  service: string;
  verdict: 'works' | 'degraded' | 'fails' | 'nodata';
  /** Reason with figures in backticks: "Latency `665 ms` on satellite vs `100 ms` required" */
  reason?: string;
  /** Shown in the expanded panel, one SourceLine each */
  sources?: ServiceSource[];
  /** Path rule and version, e.g. "Best path: satellite (NBN residual) · rule `v1`" */
  path?: string;
  defaultExpanded?: boolean;
  /** Typically an AssumptionNote for Degraded verdicts */
  children?: React.ReactNode;
}
export function ServiceRow(props: ServiceRowProps): JSX.Element;
