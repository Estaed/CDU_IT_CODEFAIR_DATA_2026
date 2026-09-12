/** Light footer with a hairline top rule: one attribution line per source, the team line and the plain statement. */
export interface FooterProps {
  /** One line per source, e.g. "ACCC Mobile Infrastructure Report 2025 · CC BY 4.0 · `2025-11-10`" (backticks set figures in mono). */
  attributions?: string[];
  team?: string;
  statement?: string;
}
export function Footer(props: FooterProps): JSX.Element;
