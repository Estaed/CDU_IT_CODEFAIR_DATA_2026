/** Search field for the 96 communities with a result list beneath it. Matches by name or alias. */
export interface SearchResult { id?: string; name: string; aliases?: string[]; region?: string; population?: number }
export interface SearchInputProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  /** Rows to show beneath the input; empty array hides the list. */
  results?: SearchResult[];
  onSelect?: (result: SearchResult) => void;
  /** Accessible label; the field has no visible label. */
  label?: string;
}
export function SearchInput(props: SearchInputProps): JSX.Element;
