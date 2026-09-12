/** 56px top bar: app title at left, optional controls in the middle, offline indicator chip at right. Sticky by default. */
export interface TopBarProps {
  title?: string;
  /** Renders "Offline" (true) or "Online" (false) as a grey chip; the word carries the state, not a colour. */
  offline?: boolean;
  sticky?: boolean;
  children?: React.ReactNode;
}
export function TopBar(props: TopBarProps): JSX.Element;
