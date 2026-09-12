/** Grey pill for a service present, a fragility flag or a colour-by choice. Tappable when onClick is given (44px hit area). */
export interface ChipProps {
  children?: React.ReactNode;
  /** Makes the chip a 44px-tall button. */
  onClick?: () => void;
  /** Selected chips invert to the near-black primary. */
  selected?: boolean;
}
export function Chip(props: ChipProps): JSX.Element;
