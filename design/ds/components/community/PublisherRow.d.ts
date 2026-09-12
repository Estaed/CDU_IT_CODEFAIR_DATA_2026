/** One published claim about mobile coverage: publisher, kind chip, says-covered badge, detail line and source line. */
export interface PublisherRowProps {
  publisher: string;
  /** predicted (carrier polygon) · licensed (ACMA site within 5 km) · listed (NTG 2022 list) · portal (BushTel row) */
  kind: 'predicted' | 'licensed' | 'listed' | 'portal';
  saysCovered: 'covered' | 'not-covered' | 'not-recorded';
  /** Detail with figures in backticks, e.g. "Telstra site at `0.06 km`, 74 Perdjert Street". Predicted rows get "(carrier prediction)" appended. */
  detail?: string;
  source?: string;
  date?: string;
}
export function PublisherRow(props: PublisherRowProps): JSX.Element;
