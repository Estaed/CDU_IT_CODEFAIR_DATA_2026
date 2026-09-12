/** The line beneath every value that came from somewhere: source name, middle dot, ISO date in mono. */
export interface SourceLineProps {
  /** Optional prefix, e.g. "Failing figure:" */
  label?: string;
  /** Source name; renders "Not recorded" when empty. */
  source?: string;
  /** ISO date YYYY-MM-DD */
  date?: string;
}
export function SourceLine(props: SourceLineProps): JSX.Element;
