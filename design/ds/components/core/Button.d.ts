/**
 * Primary or secondary action. One near-black primary per screen; never a coloured button.
 * @startingPoint section="Core" subtitle="Primary and secondary buttons" viewport="360x120"
 */
export interface ButtonProps {
  /** 'primary' is the near-black fill; 'secondary' is white with a hairline border. */
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  /** Full width on phone layouts. */
  fullWidth?: boolean;
  onClick?: () => void;
  children?: React.ReactNode;
}
export function Button(props: ButtonProps): JSX.Element;
