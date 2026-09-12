/** A horizontally scrolling row of tabs. Selection is shown by ink text and a 2px bottom rule; tabs never wrap or shrink. */
export interface FilterTab { id: string; label: string; /** optional mono count after the label */ count?: number }
export interface FilterTabsProps {
  tabs: FilterTab[];
  selected?: string;
  onSelect?: (id: string) => void;
  ariaLabel?: string;
}
export function FilterTabs(props: FilterTabsProps): JSX.Element;
