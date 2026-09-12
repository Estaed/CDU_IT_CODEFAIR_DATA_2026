/** Prose with every figure set in monospace. Mark figures with backticks in `text`. */
export interface FiguresProps {
  /** e.g. "Latency `665 ms` on satellite vs `100 ms` required" */
  text: string;
  /** Mono size to match the surrounding sans size: xs 13px, sm 14px, md 16px, lg 22px. */
  size?: 'xs' | 'sm' | 'md' | 'lg';
}
export function Figures(props: FiguresProps): JSX.Element;
